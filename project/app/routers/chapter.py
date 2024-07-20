from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Chapter, ChapterCreate, ChapterRead, ChapterUpdate,ChapterReadOneCikaran
from sqlalchemy.orm import joinedload

router = APIRouter()

@router.post("/{manga_id}/chapter", response_model=ChapterRead)
async def create_chapter_for_manga(manga_id: int, chapter: ChapterCreate, session: Session = Depends(get_session)):
    db_chapter = Chapter.from_orm(chapter)
    db_chapter.manga_id = manga_id
    session.add(db_chapter)
    await session.commit()
    await session.refresh(db_chapter)
    return db_chapter

@router.get("/manga/{manga_id}/chaptersall", response_model=List[ChapterRead])
async def read_chapters_for_manga(manga_id: int, session: Session = Depends(get_session)):
    result = await session.exec(select(Chapter).where(Chapter.manga_id == manga_id))
    chapters = result.all()
    return chapters

@router.put("/chapter/{chapter_id}", response_model=ChapterRead)
async def update_chapter(chapter_id: int, chapter: ChapterUpdate, session: Session = Depends(get_session)):
    db_chapter = await session.get(Chapter, chapter_id)
    if not db_chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    chapter_data = chapter.dict(exclude_unset=True)
    for key, value in chapter_data.items():
        setattr(db_chapter, key, value)
    session.add(db_chapter)
    await session.commit()
    await session.refresh(db_chapter)
    return db_chapter


@router.delete("/chapter/{chapter_id}")
async def delete_chapter(chapter_id: int, session: Session = Depends(get_session)):
    db_chapter = await session.get(Chapter, chapter_id)
    chaptered = db_chapter.scalar_one_or_none()
    if not db_chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    await session.delete(chaptered)
    await session.commit()
    return {"ok": True}

@router.get("/chapters/{chapter_id}/images", response_model=List[str])
async def get_chapter_images(chapter_id: int, session: Session = Depends(get_session)):
    chapter = await session.get(Chapter, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter.get_images()

@router.get("/latest-chapters/", response_model=List[ChapterReadOneCikaran])
async def get_latest_chapters(limit: int = 6, session: Session = Depends(get_session)):
    result = await session.execute(
        select(Chapter)
        .options(joinedload(Chapter.manga))
        .order_by(Chapter.release_date.desc())
        .limit(limit)
    )
    latest_chapters = result.scalars().all()

    # ChapterReadWithoutImages modeline manga başlıklarını ekleyelim
    latest_chapters_with_titles = [
        ChapterReadOneCikaran(
            title=chapter.title,
            chapter_number=chapter.chapter_number,
            manga_id=chapter.manga_id,
            release_date=chapter.release_date,
            is_public=chapter.is_public,
            manga_title=chapter.manga.title if chapter.manga else None
        )
        for chapter in latest_chapters
    ]

    return latest_chapters_with_titles