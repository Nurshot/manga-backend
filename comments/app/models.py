from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Comment(BaseModel):
    user_id: int
    username: str
    manga_id: int
    text: str
    created_at: datetime = datetime.utcnow()