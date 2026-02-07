import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, Form
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from fastapi.middleware.cors import CORSMiddleware


from app.db import engine, init_db
from app.llm import build_llm_client
from app.models import Image
from app.schemas import ImageRead, ImageReviewRequest, ImageReviewResponse

load_dotenv()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Photo Manager", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEBUG = True


def get_session() -> Session:
    with Session(engine) as session:
        yield session


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/images", response_model=ImageRead)
async def upload_image(
    file: UploadFile = File(...),
   subject: str | None = Form(None),
    owner_name: str | None = Form(None),
    location: str | None = Form(None),
    guide_name: str | None = Form(None),
    notes: str | None = Form(None),
    session: Session = Depends(get_session),
) -> ImageRead:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="הקובץ חייב להיות תמונה")
    
    if DEBUG:
        print("subject:", subject)

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = file.filename.replace(" ", "_")
    stored_name = f"{timestamp}_{safe_name}"
    stored_path = UPLOAD_DIR / stored_name

    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image = Image(
        filename=file.filename,
        content_type=file.content_type,
        subject=subject,
        owner_name=owner_name,
        location=location,
        guide_name=guide_name,
        notes=notes,
        stored_path=str(stored_path),
    )
    session.add(image)
    session.commit()
    session.refresh(image)

    return ImageRead(**image.model_dump())


@app.get("/images", response_model=list[ImageRead])
def list_images(
    subject: Optional[str] = None,
    owner_name: Optional[str] = None,
    location: Optional[str] = None,
    guide_name: Optional[str] = None,
    uploaded_from: Optional[datetime] = Query(default=None),
    uploaded_to: Optional[datetime] = Query(default=None),
    session: Session = Depends(get_session),
) -> list[ImageRead]:
    query = select(Image)

    if subject:
        query = query.where(Image.subject == subject)
    if owner_name:
        query = query.where(Image.owner_name == owner_name)
    if location:
        query = query.where(Image.location == location)
    if guide_name:
        query = query.where(Image.guide_name == guide_name)
    if uploaded_from:
        query = query.where(Image.uploaded_at >= uploaded_from)
    if uploaded_to:
        query = query.where(Image.uploaded_at <= uploaded_to)

    images = session.exec(query).all()
    return [ImageRead(**image.model_dump()) for image in images]


@app.get("/images/{image_id}", response_model=ImageRead)
def get_image(image_id: int, session: Session = Depends(get_session)) -> ImageRead:
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="תמונה לא נמצאה")
    return ImageRead(**image.model_dump())


@app.get("/images/{image_id}/file")
def get_image_file(image_id: int, session: Session = Depends(get_session)) -> FileResponse:
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="תמונה לא נמצאה")

    file_path = Path(image.stored_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="קובץ תמונה לא נמצא")

    return FileResponse(file_path, media_type=image.content_type, filename=image.filename)


@app.post("/images/{image_id}/review", response_model=ImageReviewResponse)
async def review_image(
    image_id: int,
    payload: ImageReviewRequest,
    session: Session = Depends(get_session),
) -> ImageReviewResponse:
    image = session.get(Image, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="תמונה לא נמצאה")

    prompt = (
        "נתוני התמונה:\n"
        f"שם קובץ: {image.filename}\n"
        f"נושא: {image.subject or 'לא צוין'}\n"
        f"בעלים: {image.owner_name or 'לא צוין'}\n"
        f"מיקום: {image.location or 'לא צוין'}\n"
        f"מדריך: {image.guide_name or 'לא צוין'}\n"
        f"הערות: {image.notes or 'אין'}\n\n"
        "הנחיות ביקורת:\n"
        f"קריטריונים: {payload.criteria}\n"
        f"טון: {payload.tone}\n"
        f"שפה: {payload.language}\n"
    )

    client = build_llm_client()
    review, model = await client.review_image(prompt)

    image.llm_review = review
    image.llm_reviewed_at = datetime.utcnow()
    session.add(image)
    session.commit()

    return ImageReviewResponse(image_id=image.id, review=review, model=model)
