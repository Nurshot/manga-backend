from fastapi import APIRouter, HTTPException, Depends, UploadFile, File,Query, Response
from sqlmodel import Session,  select,func,delete
from sqlalchemy.future import select
from typing import List
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_session
from typing import List, Optional
from ..models import Manga, MangaCreate, MangaRead, MangaUpdate, MangaCategoryLink,Chapter,ChapterRead,ChapterUpdate,ChapterReadWithImages,ChapterReadWithoutImages,ChapterUpdatewithImages
import zipfile
import io
import base64
import json
import re
from fastapi.responses import JSONResponse



router = APIRouter()

@router.post("/manga/", response_model=MangaRead)
async def create_manga(manga: MangaCreate, session: Session = Depends(get_session)):
    async with session.begin():
        db_manga = Manga.from_orm(manga)
        session.add(db_manga)
    
    await session.commit()
    await session.refresh(db_manga)

    for category_id in manga.category_ids:
        link = MangaCategoryLink(manga_id=db_manga.id, category_id=category_id)
        session.add(link)
    
    await session.commit()
    await session.refresh(db_manga)

    query = select(Manga).where(Manga.id == db_manga.id).options(selectinload(Manga.categories))
    result = await session.execute(query)
    manga_with_categories = result.scalar_one_or_none()
    if not manga_with_categories:
        raise HTTPException(status_code=404, detail="Manga not found")

    return manga_with_categories


@router.get("/manga/", response_model=List[MangaRead])
async def read_mangas(
    response: Response,
    skip: Optional[int] = Query(None),
    limit: Optional[int] = Query(None),
    session: Session = Depends(get_session)
):
    total_result = await session.execute(select(Manga))
    total = len(total_result.scalars().all())

    query = select(Manga).options(selectinload(Manga.categories))
    
    if skip is not None:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
        
    result = await session.execute(query)
    mangas = result.scalars().all()

    # X-Total-Count başlığını yanıtın başlıklarına ekle
    response.headers['X-Total-Count'] = str(total)
    
    return mangas

@router.get("/manga/{manga_id}", response_model=MangaRead)
async def read_manga(manga_id: int, session: Session = Depends(get_session)):
    query = select(Manga).where(Manga.id == manga_id).options(selectinload(Manga.categories))
    result = await session.execute(query)
    manga = result.scalar_one_or_none()
    manga.read_count += 1
    session.add(manga)
    await session.commit()

    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    return manga

@router.put("/manga/{manga_id}")
async def update_mangaa(manga_id: int, update_request: MangaUpdate, session: Session = Depends(get_session)):
    
    db_manga = await session.get(Manga, manga_id)
    if not db_manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    if update_request.category_ids is not None:
        # Mevcut tüm bağlantıları sil
        await session.execute(delete(MangaCategoryLink).where(MangaCategoryLink.manga_id == manga_id))
        # Yeni bağlantıları ekle
        for category_id in update_request.category_ids:
            link = MangaCategoryLink(manga_id=db_manga.id, category_id=category_id)
            session.add(link)


    db_manga.title = update_request.title
    db_manga.author = update_request.author
    db_manga.description = update_request.description
    db_manga.cover_image = update_request.cover_image
    

    session.add(db_manga)
    await session.commit()
    await session.refresh(db_manga)

    return {"message": "Mangas updated successfully"}

# @router.put("/manga/{manga_id}", response_model=Manga)
# async def update_manga(manga_id: int, manga: MangaUpdate, session: AsyncSession = Depends(get_session)):
    
#     db_manga = await session.get(Manga, manga_id)
#     if not db_manga:
#         raise HTTPException(status_code=404, detail="Manga not found")

#     # Önce kategori bağlantılarını güncelleyin
#     if manga.category_ids is not None:
#         await session.execute(delete(MangaCategoryLink).where(MangaCategoryLink.manga_id == manga_id))
#         for category_id in manga.category_ids:
#             link = MangaCategoryLink(manga_id=db_manga.id, category_id=category_id)
#             session.add(link)

#     # Sonra diğer alanları güncelleyin
#     update_data = manga.dict(exclude_unset=True, exclude={"category_ids"})
#     for key, value in update_data.items():
#         setattr(db_manga, key, value)

#     await session.commit()
#     await session.refresh(db_manga)

#     return {"message": "Chapter deleted successfully"}






@router.delete("/manga/{manga_id}")
async def delete_manga(manga_id: int, session: Session = Depends(get_session)):
    async with session.begin():
        db_manga = await session.get(Manga, manga_id)
        if not db_manga:
            raise HTTPException(status_code=404, detail="Manga not found")
        await session.delete(db_manga)
    
    await session.commit()
    return {"ok": True}

@router.post("/manga/{manga_id}/upload_chapters")
async def upload_chapters(manga_id: int, zip_file: UploadFile = File(...), session: Session = Depends(get_session)):
    manga = await session.get(Manga, manga_id)
    if not manga:
        raise HTTPException(status_code=404, detail="Manga not found")
    
    # ZIP dosyasını oku ve ayıkla
    zip_bytes = await zip_file.read()
    zip_data = io.BytesIO(zip_bytes)
    with zipfile.ZipFile(zip_data, 'r') as zip_ref:
        chapter_folders = [f for f in zip_ref.namelist() if f.endswith('/')]
        for chapter_folder in chapter_folders:
            match = re.search(r'\d+', chapter_folder)
            if not match:
                continue
            chapter_number = int(match.group())
            db_chapter = Chapter(title=f"Chapter {chapter_number}", chapter_number=chapter_number, manga_id=manga_id)
            session.add(db_chapter)
            await session.commit()
            await session.refresh(db_chapter)

            images = []
            image_files = sorted(
                [f for f in zip_ref.namelist() if f.startswith(chapter_folder) and not f.endswith('/')],
                key=lambda x: (int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf'), x)
            )
            for file_name in image_files:
                if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_data = zip_ref.read(file_name)
                    image_base64 = base64.b64encode(image_data).decode('utf-8')
                    images.append(image_base64)

            db_chapter.set_images(images)
            session.add(db_chapter)
            await session.commit()

    return {"message": "Chapters uploaded successfully"}

@router.get("/manga/{manga_id}/chapters", response_model=List[ChapterReadWithoutImages])
async def get_chapters(manga_id: int, session: Session = Depends(get_session)):
    result = await session.execute(select(Chapter).where(Chapter.manga_id == manga_id))
    chapters = result.scalars().all()
    return chapters


@router.get("/manga/{manga_id}/chapter/{chapter_number}/images", response_model=ChapterReadWithImages)
async def get_chapter_images(manga_id: int, chapter_number: int, session: Session = Depends(get_session)):
    result = await session.execute(select(Chapter).where(Chapter.manga_id == manga_id, Chapter.chapter_number == chapter_number))
    chapter = result.scalars().one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    try:
        images = json.loads(chapter.images)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse images")

    return JSONResponse(
        status_code=200,
        content={"images": images},
    )

@router.put("/manga/{manga_id}/chapter/{chapter_number}/images")
async def update_chapter_images(manga_id: int, chapter_number: int, update_request: ChapterUpdatewithImages, session: Session = Depends(get_session)):
    chapter = await session.execute(select(Chapter).where(Chapter.manga_id == manga_id, Chapter.chapter_number == chapter_number))
    chapter = chapter.scalars().one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    try:
        chapter.images = json.dumps(update_request.images)
        session.add(chapter)
        await session.commit()
        await session.refresh(chapter)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to update images")

    return {"message": "Images updated successfully"}

@router.delete("/manga/{manga_id}/chapter/{chapter_id}/images/{image_index}")
async def delete_chapter_image(manga_id: int, chapter_id: int, image_index: int, session: Session = Depends(get_session)):
    chapter = await session.get(Chapter, chapter_id)
    if not chapter or chapter.manga_id != manga_id:
        raise HTTPException(status_code=404, detail="Chapter not found")

    try:
        images = json.loads(chapter.images)
        if 0 <= image_index < len(images):
            images.pop(image_index)
            chapter.images = json.dumps(images)
            session.add(chapter)
            await session.commit()
            await session.refresh(chapter)
        else:
            raise HTTPException(status_code=404, detail="Image not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to update images")

    return {"message": "Image deleted successfully"}
    
@router.delete("/manga/{manga_id}/chapter/{chapter_number}")
async def update_chapter_images(manga_id: int, chapter_number: int,  session: Session = Depends(get_session)):
    chapter = await session.execute(select(Chapter).where(Chapter.manga_id == manga_id, Chapter.chapter_number == chapter_number))
    chapter = chapter.scalars().one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    await session.delete(chapter)
    await session.commit()
    return {"ok": True}
