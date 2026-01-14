from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Vendor
from typing import List

router = APIRouter(prefix="/vendors", tags=["Vendors"])

@router.post("/", response_model=Vendor)
async def create_vendor(vendor: Vendor, session: Session = Depends(get_session)):
    session.add(vendor)
    session.commit()
    session.refresh(vendor)
    return vendor

@router.get("/", response_model=List[Vendor])
async def list_vendors(session: Session = Depends(get_session)):
    statement = select(Vendor)
    results = session.exec(statement)
    return results.all()

@router.get("/{vendor_id}", response_model=Vendor)
async def get_vendor(vendor_id: int, session: Session = Depends(get_session)):
    vendor = session.get(Vendor, vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor
