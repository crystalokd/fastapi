import time
from typing import List

import psycopg
from fastapi import FastAPI, HTTPException, Response, status
from psycopg.rows import dict_row
from pydantic import BaseModel

app = FastAPI()


# Define your Pydantic model
class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Database connection
while True:
    try:
        conn = psycopg.connect(
            host="localhost",
            dbname="fastapi",
            user="postgres",
            password="postgres",
            row_factory=dict_row,
        )
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error:", error)
        time.sleep(2)


my_posts = [
    {"title": "...", "content": "...", "id": 1},
    {"title": "222", "content": "222", "id": 2},
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


# Endpoints
@app.get("/")
def root():
    return {"Hello": "World..."}


@app.get("/posts", response_model=List[Post])
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=Post)
def create_post(post: Post):
    cursor.execute(
        "INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *",
        (post.title, post.content, post.published),
    )
    new_post = cursor.fetchone()
    conn.commit()
    return new_post


@app.get("/posts/{post_id}", response_model=Post)
def get_post(post_id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (post_id,))
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (post_id,))
    deleted_post = cursor.fetchone()
    if deleted_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}", response_model=Post)
def update_post(post_id: int, post: Post):
    cursor.execute(
        "UPDATE posts SET title = %s, content = %s, published = %s, rating = %s WHERE id = %s RETURNING *",
        (post.title, post.content, post.published, post.rating, post_id),
    )
    updated_post = cursor.fetchone()
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    conn.commit()
    return updated_post
