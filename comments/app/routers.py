from fastapi import APIRouter, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from .models import Comment
from bson import ObjectId
from typing import List, Optional

comment_router = APIRouter()

client = AsyncIOMotorClient("mongodb://mongo:27017")
db = client.comments_db

@comment_router.post("/", response_model=Comment)
async def create_comment(comment: Comment):
    comment_dict = comment.dict()
    comment_dict["_id"] = str(ObjectId())
    result = await db.comments.insert_one(comment_dict)
    if result.inserted_id:
        return comment
    raise HTTPException(status_code=400, detail="Comment could not be created")

@comment_router.get("/", response_model=List[Comment])
async def get_comments(manga_id: int):
    comments = await db.comments.find({"manga_id": manga_id}).to_list(100)
    return [Comment(**comment) for comment in comments]