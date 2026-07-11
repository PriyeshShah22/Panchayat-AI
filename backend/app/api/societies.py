"""Society / Block / Flat router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.society import Block, Flat, Society
from app.schemas.society import (
    BlockCreate, BlockOut, FlatCreate, FlatOut, SocietyCreate, SocietyOut,
)

router = APIRouter(prefix="/societies", tags=["societies"])


@router.get("/", response_model=list[SocietyOut])
def list_societies(db: Session = Depends(get_db),
                   current=Depends(get_current_user)) -> list[SocietyOut]:
    rows = db.execute(select(Society).limit(100)).scalars().all()
    return [SocietyOut.model_validate(s) for s in rows]


@router.post("/", response_model=SocietyOut, status_code=status.HTTP_201_CREATED)
def create_society(payload: SocietyCreate, db: Session = Depends(get_db),
                   current=Depends(get_current_user)) -> SocietyOut:
    require_any_role(current, ["admin"])
    society = Society(**payload.model_dump())
    db.add(society)
    db.commit()
    db.refresh(society)
    return SocietyOut.model_validate(society)


@router.get("/{society_id}/blocks", response_model=list[BlockOut])
def list_blocks(society_id: int, db: Session = Depends(get_db),
                current=Depends(get_current_user)) -> list[BlockOut]:
    rows = db.execute(select(Block).where(Block.society_id == society_id)).scalars().all()
    return [BlockOut.model_validate(b) for b in rows]


@router.post("/blocks", response_model=BlockOut, status_code=status.HTTP_201_CREATED)
def create_block(payload: BlockCreate, db: Session = Depends(get_db),
                 current=Depends(get_current_user)) -> BlockOut:
    require_any_role(current, ["admin", "committee"])
    block = Block(**payload.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return BlockOut.model_validate(block)


@router.get("/blocks/{block_id}/flats", response_model=list[FlatOut])
def list_flats(block_id: int, db: Session = Depends(get_db),
               current=Depends(get_current_user)) -> list[FlatOut]:
    rows = db.execute(select(Flat).where(Flat.block_id == block_id)).scalars().all()
    return [FlatOut.model_validate(f) for f in rows]


@router.post("/flats", response_model=FlatOut, status_code=status.HTTP_201_CREATED)
def create_flat(payload: FlatCreate, db: Session = Depends(get_db),
                current=Depends(get_current_user)) -> FlatOut:
    require_any_role(current, ["admin", "committee"])
    flat = Flat(**payload.model_dump())
    db.add(flat)
    db.commit()
    db.refresh(flat)
    return FlatOut.model_validate(flat)
