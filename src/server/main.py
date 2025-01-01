from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from typing import List, Optional
from datetime import datetime

from .models import (
    TranscriptionDetails,
    TranscriptionCreate,
    EvaluationResult,
    EvaluationResultCreate,
    TranscriptionEvaluation
)
from .database import get_db, Transcription, Evaluation

app = FastAPI(title="Call Center Analytics API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Transcription endpoints
@app.post("/transcriptions/", response_model=TranscriptionDetails)
async def create_transcription(
    transcription: TranscriptionCreate,
    db: Session = Depends(get_db)
):
    db_transcription = Transcription(
        id=str(uuid.uuid4()),
        **transcription.dict()
    )
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    return db_transcription

@app.get("/transcriptions/", response_model=List[TranscriptionDetails])
async def list_transcriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    transcriptions = db.query(Transcription).offset(skip).limit(limit).all()
    return transcriptions

@app.get("/transcriptions/{transcription_id}", response_model=TranscriptionEvaluation)
async def get_transcription(transcription_id: str, db: Session = Depends(get_db)):
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return {
        "details": transcription,
        "evaluationResults": transcription.evaluations
    }

@app.delete("/transcriptions/{transcription_id}")
async def delete_transcription(transcription_id: str, db: Session = Depends(get_db)):
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    db.delete(transcription)
    db.commit()
    return {"message": "Transcription deleted"}

# Evaluation endpoints
@app.post("/transcriptions/{transcription_id}/evaluations/", response_model=EvaluationResult)
async def create_evaluation(
    transcription_id: str,
    evaluation: EvaluationResultCreate,
    db: Session = Depends(get_db)
):
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")

    db_evaluation = Evaluation(
        id=str(uuid.uuid4()),
        transcription_id=transcription_id,
        **evaluation.dict()
    )
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation

@app.get("/transcriptions/{transcription_id}/evaluations/", response_model=List[EvaluationResult])
async def list_evaluations(
    transcription_id: str,
    db: Session = Depends(get_db)
):
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if not transcription:
        raise HTTPException(status_code=404, detail="Transcription not found")
    
    return transcription.evaluations

@app.get("/evaluations/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return evaluation

@app.put("/evaluations/{evaluation_id}", response_model=EvaluationResult)
async def update_evaluation(
    evaluation_id: str,
    evaluation_update: EvaluationResultCreate,
    db: Session = Depends(get_db)
):
    db_evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not db_evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    for key, value in evaluation_update.dict().items():
        setattr(db_evaluation, key, value)
    
    db_evaluation.updated_at = datetime.now()
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation

@app.delete("/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    
    db.delete(evaluation)
    db.commit()
    return {"message": "Evaluation deleted"}

# Analytics endpoints
@app.get("/analytics/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    total_transcriptions = db.query(Transcription).count()
    total_evaluations = db.query(Evaluation).count()
    
    status_counts = (
        db.query(Evaluation.status, db.func.count(Evaluation.id))
        .group_by(Evaluation.status)
        .all()
    )
    
    successful_calls = (
        db.query(db.func.count(Transcription.id))
        .filter(Transcription.successfulCall == True)
        .scalar()
    )
    
    return {
        "total_transcriptions": total_transcriptions,
        "total_evaluations": total_evaluations,
        "evaluation_status_distribution": dict(status_counts),
        "successful_calls": successful_calls
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 