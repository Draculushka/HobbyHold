from fastapi import FastAPI, Depends, Request, Form, UploadFile, File, HTTPException, status, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base, Hobby, Tag, User
from . import schemas
import shutil
import uuid
import os
import bleach
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

# Create tables on startup
Base.metadata.create_all(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# --- Security Utils ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        # Token format is "Bearer <token>"
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user

# --- Routes ---

# --- Search Mapping ---
HOBBY_SYNONYMS = {
    "шахматы": ["chess", "шахматы"],
    "chess": ["chess", "шахматы"],
    "вархаммер": ["warhammer", "40k", "age of sigmar", "вархаммер"],
    "warhammer": ["warhammer", "40k", "age of sigmar", "вархаммер"],
    "40k": ["warhammer", "40k", "вархаммер"],
    "фотография": ["photo", "photography", "фото", "фотография"],
    "photo": ["photo", "photography", "фото", "фотография"],
    "photography": ["photo", "photography", "фото", "фотография"],
    "кулинария": ["cooking", "food", "еда", "кулинария"],
    "cooking": ["cooking", "food", "еда", "кулинария"],
    "йога": ["yoga", "йога"],
    "yoga": ["yoga", "йога"],
    "программирование": ["coding", "programming", "code", "программирование"],
    "programming": ["coding", "programming", "code", "программирование"],
    "coding": ["coding", "programming", "code", "программирование"]
}

@app.get("/")
async def home(request: Request, page: int = 1, search: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    limit = 10
    offset = (page - 1) * limit
    
    query = db.query(Hobby)
    if search:
        search_lower = search.lower().strip()
        search_terms = HOBBY_SYNONYMS.get(search_lower, [search_lower])
        
        from sqlalchemy import or_
        filters = [Hobby.title.ilike(f"%{term}%") for term in search_terms]
        query = query.filter(or_(*filters))
        
    hobbies = query.order_by(Hobby.created_at.desc()).offset(offset).limit(limit).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "hobbies": hobbies, "page": page, "search": search, "user": current_user}
    )

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login")
def login_page(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.post("/login")
def login_for_access_token(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse("/login?error=Invalid credentials", status_code=status.HTTP_303_SEE_OTHER)
    
    access_token = create_access_token(data={"sub": user.username})
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("access_token")
    return response

@app.post("/create-hobby")
async def create_hobby(
    title: str = Form(...),
    description: str = Form(...),
    tags_input: str = Form(""),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    image_filename = None
    if image and image.filename:
        # Security fix: sanitize filename
        safe_filename = Path(image.filename).name
        image_filename = f"{uuid.uuid4()}_{safe_filename}"
        path = UPLOAD_DIR / image_filename
        with open(path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    # Security fix: sanitize HTML description
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li', 'br']
    clean_description = bleach.clean(description, tags=allowed_tags, strip=True)

    hobby = Hobby(
        author=current_user.username,
        author_id=current_user.id,
        title=title,
        description=clean_description,
        image_path=image_filename,
        created_at=datetime.now(timezone.utc)
    )

    if tags_input:
        tag_names = [name.strip() for name in tags_input.split(",") if name.strip()]
        for name in tag_names:
            tag = db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
            hobby.tags.append(tag)

    db.add(hobby)
    db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/edit/{hobby_id}")
def edit_hobby_page(hobby_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    
    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not hobby:
        raise HTTPException(status_code=404, detail="Hobby not found")
    
    if hobby.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this hobby")

    tags_str = ", ".join([t.name for t in hobby.tags])
    return templates.TemplateResponse(
        "edit.html",
        {"request": request, "hobby": hobby, "tags_str": tags_str, "user": current_user}
    )

@app.post("/update/{hobby_id}")
def update_hobby_form(
    hobby_id: int,
    title: str = Form(...),
    description: str = Form(...),
    tags_input: str = Form(""),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if not hobby or hobby.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    hobby.title = title
    
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'p', 'ul', 'ol', 'li', 'br']
    hobby.description = bleach.clean(description, tags=allowed_tags, strip=True)
    
    hobby.tags = []
    if tags_input:
        tag_names = [name.strip() for name in tags_input.split(",") if name.strip()]
        for name in tag_names:
            tag = db.query(Tag).filter(Tag.name == name).first()
            if not tag:
                tag = Tag(name=name)
                db.add(tag)
            hobby.tags.append(tag)

    if image and image.filename:
        if hobby.image_path:
            old_path = UPLOAD_DIR / hobby.image_path
            if old_path.exists():
                old_path.unlink()

        safe_filename = Path(image.filename).name
        image_name = f"{uuid.uuid4()}_{safe_filename}"
        file_path = UPLOAD_DIR / image_name
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        hobby.image_path = image_name
    db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/delete-hobby/{hobby_id}")
def delete_hobby_form(hobby_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401)
    
    hobby = db.query(Hobby).filter(Hobby.id == hobby_id).first()
    if hobby and hobby.author_id == current_user.id:
        if hobby.image_path:
            old_path = UPLOAD_DIR / hobby.image_path
            if old_path.exists():
                old_path.unlink()
        db.delete(hobby)
        db.commit()
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
