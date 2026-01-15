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

@router.post("/compare/{rfp_id}")
async def compare_proposals_endpoint(rfp_id: int, session: Session = Depends(get_session)):
    # 1. Fetch RFP
    rfp = session.get(RFP, rfp_id)
    if not rfp:
        raise HTTPException(status_code=404, detail="RFP not found")
        
    # 2. Fetch all proposals for this RFP
    statement = select(Proposal).where(Proposal.rfp_id == rfp_id)
    proposals = session.exec(statement).all()
    
    if not proposals:
        raise HTTPException(status_code=400, detail="No proposals found for this RFP")
        
    # 3. Prepare data for AI
    proposals_data = []
    for p in proposals:
        vendor = session.get(Vendor, p.vendor_id)
        proposals_data.append({
            "vendor_id": p.vendor_id,
            "vendor_name": vendor.name if vendor else "Unknown",
            "proposal_text": p.raw_response
        })
        
    # 4. Call AI Service
    comparison_result = await ai_service.compare_proposals(rfp.description, proposals_data)
    
    return comparison_result
