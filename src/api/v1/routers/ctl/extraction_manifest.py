from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.deps import get_db
from api.schemas.extract_manifest import ExtractManifestResponse
from db.control.models import ApiExtractionManifestInstance

extraction_manifest_router = APIRouter()

@extraction_manifest_router.get("/extraction-manifest", tags=["extraction-manifest"])
def list_extraction_manifest(
    db: Annotated[Session, Depends(get_db)],
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[ExtractManifestResponse]: 

    extract_manifest_stmt = (
        select(ApiExtractionManifestInstance)
        .offset(skip)
        .limit(limit)
    )

    manifests = db.execute(extract_manifest_stmt).scalars().all()

    return [ExtractManifestResponse.model_validate(manifest) for manifest in manifests]


@extraction_manifest_router.get("/extraction-manifest/{manifest_id}", tags=["extraction-manifest"])
def get_rate_limit(
    manifest_id: int, 
    db: Annotated[Session, Depends(get_db)]
) -> ExtractManifestResponse: 

    manifest = db.execute(
        select(ApiExtractionManifestInstance)
        .where(ApiExtractionManifestInstance.id == manifest_id)
    ).scalars().first()

    if not manifest: 
        raise HTTPException(status_code=404, detail=f"extraction manifest {manifest_id} not found")

    return ExtractManifestResponse.model_validate(manifest)

    
    





        


