from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, oauth2
from app.database import SessionLocal
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# ----------------- DB Dependency -----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------------- Create Post -----------------
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    db_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return {"Post": schemas.PostSchema.model_validate({
        **db_post.__dict__,
        "owner": current_user
    }), "votes": 0}


# ----------------- Get All Posts -----------------
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = Query(10, ge=1),
    skip: int = Query(0, ge=0),
    search: str = Query("", description="Search posts by title")
):
    posts_with_votes = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .filter(models.Post.title.contains(search))
        .group_by(models.Post.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    results = []
    for post, votes in posts_with_votes:
        owner = db.query(models.User).filter(models.User.id == post.owner_id).first()
        results.append({
            "Post": schemas.PostSchema.model_validate({
                **post.__dict__,
                "owner": owner
            }),
            "votes": votes
        })

    return results


# ----------------- Get Single Post -----------------
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    post_with_votes = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .filter(models.Post.id == id)
        .group_by(models.Post.id)
        .first()
    )

    if not post_with_votes:
        raise HTTPException(status_code=404, detail=f"Post {id} not found")

    post, votes = post_with_votes
    owner = db.query(models.User).filter(models.User.id == post.owner_id).first()

    return {"Post": schemas.PostSchema.model_validate({
        **post.__dict__,
        "owner": owner
    }), "votes": votes}


# ----------------- Update Post -----------------
@router.put("/{id}", response_model=schemas.PostOut)
def update_post(
    id: int,
    updated_post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    for key, value in updated_post.dict().items():
        setattr(post, key, value)

    db.commit()
    db.refresh(post)

    votes = db.query(func.count(models.Vote.post_id)).filter(models.Vote.post_id == id).scalar()

    return {"Post": schemas.PostSchema.model_validate({
        **post.__dict__,
        "owner": current_user
    }), "votes": votes}
# ----------------- Delete Post -----------------
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {id} not found")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    db.delete(post)
    db.commit()
    return
