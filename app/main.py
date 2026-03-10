from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base, Post
from . import schemas
from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    posts = db.query(Post).all()

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "posts": posts}
    )
@app.post("/posts", response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = Post(
    title=post.title,
    description=post.description,
    image_path=post.image_path
)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

@app.get("/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

@app.get("/posts/{post_id}", response_model=schemas.Post)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    return post

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()

    if post:
        db.delete(post)
        db.commit()
        return {"message": "Post deleted"}

    return {"error": "Post not found"}

@app.put("/posts/{post_id}", response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if db_post:
        db_post.title = post.title
        db_post.description = post.description

        db.commit()
        db.refresh(db_post)

        return db_post

    return {"error": "Post not found"}

@app.post("/upload")
def upload_image(file: UploadFile = File(...)):
    file_path = f"app/uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename}
