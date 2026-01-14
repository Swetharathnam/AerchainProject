from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import RFP, RFPStatus
from services.ai_service import ai_service
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/rfps", tags=["RFPs"])

class RFPCreateRequest(BaseModel):
    natural_language_input: str

class RFPResponse(BaseModel):
    id: int
    title: str
    description: str
    budget: Optional[float]
    status: RFPStatus
    structured_data: Optional[str]

@router.post("/generate")
async def generate_rfp_structure(request: RFPCreateRequest):
    """
    Takes natural language input and uses AI to return a suggested structure.
    Does NOT save to DB yet (preview mode).
    """
    structured_data = await ai_service.extract_rfp_structure(request.natural_language_input)
    return structured_data

@router.post("/", response_model=RFP)
async def create_rfp(rfp_data: RFP, session: Session = Depends(get_session)):
    """
    Save a confirmed RFP to the database.
    """
    session.add(rfp_data)
    session.commit()
    session.refresh(rfp_data)
    return rfp_data

@router.get("/", response_model=List[RFP])
async def list_rfps(session: Session = Depends(get_session)):
    statement = select(RFP)
    results = session.exec(statement)
    return results.all()

@router.get("/{rfp_id}", response_model=RFP)
async def get_rfp(rfp_id: int, session: Session = Depends(get_session)):
    rfp = session.get(RFP, rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
    return rfp

class SendRFPRequest(BaseModel):
    vendor_ids: List[int]

@router.post("/{rfp_id}/send")
async def send_rfp_to_vendors(
    rfp_id: int, 
    request: SendRFPRequest, 
    session: Session = Depends(get_session)
):
    from services.email_service import email_service
    from models import Vendor, VendorRFPLink
    
    rfp = session.get(RFP, rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
        
    sent_count = 0
    for vendor_id in request.vendor_ids:
        vendor = session.get(Vendor, vendor_id)
        if vendor and vendor.email:
            # Construct Email Body
            subject = f"RFP: {rfp.title}"
            body = f"""
Dear {vendor.contact_person or 'Vendor'},

We are inviting you to submit a proposal for the following requirement:

{rfp.description}

Budget Indication: {rfp.budget or 'N/A'} {rfp.currency}

Please reply to this email with your best proposal.

Regards,
Procurement Team
            """
            
            # Send Email
            success = await email_service.send_email(vendor.email, subject, body)
            
            if success:
                sent_count += 1
                # Record the link
                # Check if link exists first to avoid duplicates (optional, simplified here)
                link = VendorRFPLink(vendor_id=vendor.id, rfp_id=rfp.id)
                session.add(link)
                
    rfp.status = RFPStatus.OPEN
    session.add(rfp)
    session.commit()
    
    return {"message": f"RFP sent to {sent_count} vendors", "status": "success"}
