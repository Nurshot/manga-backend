from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date
from datetime import datetime
import hashlib

class UserBase(SQLModel):
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False

class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str

class UserCreate(SQLModel):
    username: str
    email: str
    password: str  # Plain text password for creation

class UserRead(UserBase):
    id: int

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class MangaCategoryLink(SQLModel, table=True):
    manga_id: int = Field(foreign_key="manga.id", primary_key=True)
    category_id: int = Field(foreign_key="category.id", primary_key=True)

class MangaBase(SQLModel):
    title: str
    author: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    read_count: int = Field(default=0)
    artist: Optional[str] = None
    language: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[str] = None
    publisher: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = None



class Manga(MangaBase, table=True):
    id: int = Field(default=None, primary_key=True)
    chapters: List["Chapter"] = Relationship(back_populates="manga")
    categories: List["Category"] = Relationship(
        back_populates="mangas",
        link_model=MangaCategoryLink
    )
    


class MangaCreate(MangaBase):
    category_ids: List[int] = []

class MangaRead(MangaBase):
    id: int
    categories: List["CategoryRead"]

    
class MangaUpdate(SQLModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    cover_image: Optional[str] = None
    category_ids: Optional[List[int]] = None

class ChapterBase(SQLModel):
    title: str
    chapter_number: int
    manga_id: int = Field(foreign_key="manga.id")
    release_date: Optional[datetime] = Field(default_factory=datetime.now)  # V
    is_public: bool = True
    images: str = "[]"  # JSON formatında resim yolları veya base64 kodları

class Chapter(ChapterBase, table=True):
    id: int = Field(default=None, primary_key=True)
    manga: Manga = Relationship(back_populates="chapters")

    def get_images(self) -> List[str]:
        import json
        return json.loads(self.images)

    def set_images(self, images: List[str]):
        import json
        self.images = json.dumps(images)

class ChapterCreate(ChapterBase):
    pass

class ChapterRead(ChapterBase):
    id: int

class ChapterReadWithImages(SQLModel):
    id: int
    images: List[str]  # Base64 encoded strings or URLs to images,


class ChapterUpdatewithImages(SQLModel):
    images: List[str]

class ChapterReadWithoutImages(SQLModel):
    title: str
    chapter_number: int
    manga_id: int
    release_date: Optional[datetime] = None
    is_public: bool

class ChapterReadOneCikaran(SQLModel):
    title: str
    chapter_number: int
    manga_id: int
    release_date: Optional[datetime] = None
    is_public: bool
    manga_title: Optional[str] = None


class ChapterUpdate(SQLModel):
    title: Optional[str] = None
    chapter_number: Optional[int] = None
    manga_id: Optional[int] = None
    release_date: Optional[date] = None
    is_public: Optional[bool] = None
    images: Optional[List[str]] = None

    def set_images(self, images: List[str]):
        import json
        self.images = json.dumps(images)

class CategoryBase(SQLModel):
    name: str
    description: Optional[str] = None

class Category(CategoryBase, table=True):
    id: int = Field(default=None, primary_key=True)
    mangas: List[Manga] = Relationship(
        back_populates="categories",
        link_model=MangaCategoryLink
    )

class CategoryCreate(CategoryBase):
    pass

class CategoryRead(CategoryBase):
    id: int
    name: str


class CategoryUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None

class MangaReadCat(SQLModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    read_count: int
    categories: Optional[List["CategoryRead"]] = []

class CategoryReadWithId(CategoryBase):
    id: int
    mangas: List[MangaReadCat] = []


