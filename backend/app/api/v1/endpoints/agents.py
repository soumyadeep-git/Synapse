from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any
import logging

from app.core.celery_app import celery_app
from app.tasks.agent_tasks import run_autonomous_investigation

router = APIRouter()
logger = logging.getLogger(__name__)

# Define the Input Schema
class IncidentRequest(BaseModel):
    description: str  # e.g. "High latency on API detected in logs"

# Define the Output Schema
class TaskResponse(BaseModel):
    task_id: str
    status: str

@router.post("/investigate", response_model=TaskResponse)
def trigger_investigation(
    request: IncidentRequest,
    # user: dict = Depends(get_current_user) # Add auth later
) -> Any:
    """
    Triggers the autonomous agent to investigate an incident.
    Returns a Task ID immediately (non-blocking).
    """
    logger.info(f"Received investigation request: {request.description}")
    
    # 1. Trigger the Celery Task
    # .delay() is the magic method that pushes it to Redis
    task = run_autonomous_investigation.delay(request.description)
    
    return {
        "task_id": task.id,
        "status": "processing"
    }

@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """
    Checks the status of a running agent.
    """
    task_result = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return response