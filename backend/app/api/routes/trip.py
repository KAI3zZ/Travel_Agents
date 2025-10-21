"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.multi_agents import get_multi_agents

router = APIRouter(prefix="/trip",tags=["旅行计划"])

@router.post(
    
)