from fastapi import FastAPI, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import engine, get_db
from .models import Base, Post
from . import schemas

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
        description=post.description
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@app.get("/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

