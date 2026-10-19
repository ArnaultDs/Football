from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.deps import get_db
from api.schemas.rate_limit import RateLimitResponse
from db.control.models import RapidApiLimiterInstance

rate_limiter_router = APIRouter()

@rate_limiter_router.get("/rate-limits", tags=["rate-limits"])
def list_rate_limit(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[RateLimitResponse]: 

    rate_limit_stmt = (
        select(RapidApiLimiterInstance)
        .offset(skip)
        .limit(limit)
    )

    rate_limits = db.execute(rate_limit_stmt).scalars().all()

    return [RateLimitResponse.model_validate(rate_limit) for rate_limit in rate_limits]


@rate_limiter_router.get("/rate-limits/{rate_limit_id}", tags=["rate-limits"])
def get_rate_limit(
    rate_limit_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> RateLimitResponse: 

    rate_limit = db.execute(
        select(RapidApiLimiterInstance)
        .where(RapidApiLimiterInstance.id == rate_limit_id)
    ).scalars().first()

    if not rate_limit: 
        raise HTTPException(status_code=404, detail=f"rate limit {rate_limit_id} not found")

    return RateLimitResponse.model_validate(rate_limit)

    
    





        


