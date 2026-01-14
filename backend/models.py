from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RFPStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    AWARDED = "awarded"

class VendorRFPLink(SQLModel, table=True):
    vendor_id: Optional[int] = Field(default=None, foreign_key="vendor.id", primary_key=True)
    rfp_id: Optional[int] = Field(default=None, foreign_key="rfp.id", primary_key=True)

class Vendor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    contact_person: Optional[str] = None
    
    rfps: List["RFP"] = Relationship(back_populates="vendors", link_model=VendorRFPLink)
    proposals: List["Proposal"] = Relationship(back_populates="vendor")

class RFP(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str # The natural language input or summarized requirement
    budget: Optional[float] = None
    currency: str = "USD"
    status: RFPStatus = Field(default=RFPStatus.DRAFT)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI Extracted Structure (stored as JSON string if needed, or specific columns)
    # For now, we'll keep it simple, but we could add a JSON/JSONB column for structured specs
    structured_data: Optional[str] = None 
    
    vendors: List[Vendor] = Relationship(back_populates="rfps", link_model=VendorRFPLink)
    proposals: List["Proposal"] = Relationship(back_populates="rfp")

class Proposal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    rfp_id: int = Field(foreign_key="rfp.id")
    vendor_id: int = Field(foreign_key="vendor.id")
    received_at: datetime = Field(default_factory=datetime.utcnow)
    
    raw_response: str # The raw email body
    extracted_data: Optional[str] = None # JSON string of AI extracted details (price, timeline, etc)
    ai_score: Optional[int] = None
    ai_rationale: Optional[str] = None
    
    rfp: RFP = Relationship(back_populates="proposals")
    vendor: Vendor = Relationship(back_populates="proposals")
