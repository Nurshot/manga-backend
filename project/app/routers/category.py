from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Category, CategoryCreate, CategoryRead, CategoryUpdate,MangaReadCat,CategoryReadWithId
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/category/", response_model=CategoryRead)
async def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    db_category = Category.from_orm(category)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category


@router.get("/category/", response_model=List[CategoryRead])
async def read_categories(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Category))
    categories = result.scalars().all()
    return categories

@router.get("/category/{category_id}", response_model=CategoryReadWithId)
async def read_category(category_id: int, session: AsyncSession = Depends(get_session)):
    query = select(Category).where(Category.id == category_id).options(selectinload(Category.mangas))
    result = await session.execute(query)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Create the response model
    category_read = CategoryReadWithId(
        id=category.id,
        name=category.name,
        description=category.description,
        mangas=[MangaReadCat(
            id=manga.id,
            title=manga.title,
            author=manga.author,
            description=manga.description,
            cover_image=manga.cover_image,
            read_count=manga.read_count,
        ) for manga in category.mangas]
    )
    
    return category_read

@router.put("/category/{category_id}", response_model=CategoryUpdate)
async def update_category(category_id: int, category: CategoryUpdate, session: Session = Depends(get_session)):
    db_category = await session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data = category.dict(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    return db_category

@router.delete("/category/{category_id}")
async def delete_category(category_id: int, session: Session = Depends(get_session)):
    db_category = await session.get(Category, category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    await session.delete(db_category)
    await session.commit()
    return {"ok": True}