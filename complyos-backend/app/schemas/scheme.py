from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class SchemeResponse(BaseModel):
    scheme_name: str
    ministry: str
    scheme_type: str
    max_benefit: str
    eligibility_match_score: int
    why_eligible: str
    required_documents: List[str]
    application_portal: str
    is_women_specific: bool
    deadline: Optional[str] = None

class SchemeApplicationCreate(BaseModel):
    scheme_name: str
    scheme_type: str
    match_score: int
    prefilled_data: Optional[Dict] = {}
