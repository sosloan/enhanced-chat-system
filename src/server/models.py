from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class EvaluationCriterion(BaseModel):
    name: str
    score: int
    rationale: str

class TranscriptionDetails(BaseModel):
    id: str
    successfulCall: bool
    classification: str
    filename: str
    created_at: datetime = datetime.now()

class EvaluationResult(BaseModel):
    id: str
    status: Literal['Needs Improvement', 'Satisfactory', 'Excellent']
    criteria: List[EvaluationCriterion]
    improvementSuggestion: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class TranscriptionEvaluation(BaseModel):
    details: TranscriptionDetails
    evaluationResults: List[EvaluationResult]

class TranscriptionCreate(BaseModel):
    successfulCall: bool
    classification: str
    filename: str

class EvaluationResultCreate(BaseModel):
    status: Literal['Needs Improvement', 'Satisfactory', 'Excellent']
    criteria: List[EvaluationCriterion]
    improvementSuggestion: Optional[str] = None 