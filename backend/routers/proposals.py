from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Proposal, RFP, Vendor
from services.ai_service import ai_service
import json

router = APIRouter(prefix="/proposals", tags=["Proposals"])

@router.post("/", response_model=Proposal)
async def create_proposal(proposal: Proposal, session: Session = Depends(get_session)):
    # 1. Validate RFP and Vendor exist
    rfp = session.get(RFP, proposal.rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
        
    vendor = session.get(Vendor, proposal.vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # 2. Trigger AI Analysis
    analysis_result = await ai_service.analyze_proposal(rfp.description, proposal.raw_response)
    
    # 3. Update Proposal with Analysis
    proposal.ai_score = analysis_result.get("score")
    proposal.ai_rationale = analysis_result.get("rationale")
    proposal.extracted_data = json.dumps(analysis_result) # Store full analysis including pros/cons

    session.add(proposal)
    session.commit()
    session.refresh(proposal)
    return proposal

@router.get("/rfp/{rfp_id}", response_model=list[Proposal])
async def list_proposals_for_rfp(rfp_id: int, session: Session = Depends(get_session)):
    statement = select(Proposal).where(Proposal.rfp_id == rfp_id)
    results = session.exec(statement)
    return results.all()
