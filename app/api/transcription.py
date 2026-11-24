
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.transcription import Transcription
from app.schemas.transcription import (
    TranscriptionCreate,
    TranscriptionUpdate,
    TranscriptionResponse
)

router = APIRouter(
    prefix="/api/transcriptions",
    tags=["Transcriptions"]
)


# CREATE
@router.post("/", response_model=TranscriptionResponse)
def create_transcription(
    data: TranscriptionCreate,
    db: Session = Depends(get_db)
):
    record = Transcription(**data.model_dump())

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# READ ALL
@router.get("/", response_model=list[TranscriptionResponse])
def get_transcriptions(db: Session = Depends(get_db)):
    return (
        db.query(Transcription)
        .order_by(Transcription.created_at.desc())
        .all()
    )


# READ ONE
@router.get("/{transcription_id}", response_model=TranscriptionResponse)
def get_transcription(
    transcription_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Transcription not found")

    return record


# UPDATE
@router.put("/{transcription_id}", response_model=TranscriptionResponse)
def update_transcription(
    transcription_id: int,
    data: TranscriptionUpdate,
    db: Session = Depends(get_db)
):
    record = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Transcription not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)

    return record


# DELETE
@router.delete("/{transcription_id}")
def delete_transcription(
    transcription_id: int,
    db: Session = Depends(get_db)
):
    record = db.query(Transcription).filter(
        Transcription.id == transcription_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Transcription not found")

    db.delete(record)
    db.commit()

    return {"message": "Transcription deleted successfully"}
