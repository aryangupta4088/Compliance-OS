import json
from langchain_groq import ChatGroq
from app.services.ocr_service import OCRService
from app.database import mongo_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, update
from app.models.compliance import ComplianceDeadline
from app.models.business import BusinessProfile
from datetime import datetime
import uuid

VEDA_PROMPT = """
You are VEDA, a document intelligence agent for Indian MSME compliance documents.
Analyze this document text and extract all important information.
Return ONLY valid JSON. No explanation. No markdown.

{
  "document_type": "GST Certificate/Udyam/Invoice/Shop License/etc",
  "registration_numbers": {
    "gstin": "", "udyam_number": "", "pan": "", "cin": "", "fssai": "", "other": []
  },
  "important_dates": [
    {
      "date": "DD/MM/YYYY",
      "type": "filing_deadline/expiry/payment/renewal",
      "description": "",
      "urgency": "high/medium/low"
    }
  ],
  "scheme_enrollments": [],
  "tax_details": { "amount": "", "period": "", "type": "" },
  "business_details": { "name": "", "address": "", "category": "" },
  "summary": "One line summary"
}

Document text:
{text}
"""

class VedAgent:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0
        )

    async def process_document(self, file_content: bytes, filename: str, user_id: str, db: AsyncSession):
        # 1. Extract Text using OCR
        text = OCRService.extract_text(file_content)
        if not text:
            return {"error": "Could not read document"}

        # 2. LLM Extraction
        response = await self.llm.ainvoke([
            ("system", "You are a precise data extraction engine."),
            ("user", VEDA_PROMPT.format(text=text))
        ])
        
        try:
            data = json.loads(response.content)
        except Exception as e:
            print(f"Veda Parse Error: {e}")
            data = {}

        # 3. Save Raw Data to MongoDB
        doc_record = {
            "user_id": user_id,
            "filename": filename,
            "raw_text": text[:5000], # Store snippet
            "extracted_data": data,
            "processed_at": datetime.utcnow(),
            "agent": "VEDA"
        }
        result = await mongo_db.documents.insert_one(doc_record)
        mongo_doc_id = str(result.inserted_id)

        # 4. Update Business Profile (Registrations)
        regs = data.get('registration_numbers', {})
        updates = {}
        if regs.get('gstin'): updates['gstin'] = regs['gstin']
        if regs.get('udyam_number'): updates['udyam_number'] = regs['udyam_number']
        if regs.get('pan'): updates['pan'] = regs['pan']
        
        if updates:
            await db.execute(
                update(BusinessProfile).where(BusinessProfile.user_id == user_id).values(**updates)
            )

        # 5. Create Deadlines in PostgreSQL
        dates = data.get('important_dates', [])
        new_deadlines = []
        for d in dates:
            try:
                # Simple date parsing assumption DD/MM/YYYY
                day, month, year = map(int, d['date'].split('/'))
                deadl = datetime(year, month, day)
                
                deadline_obj = {
                    "id": uuid.uuid4(),
                    "user_id": user_id,
                    "title": d.get('description', 'Unknown Deadline'),
                    "deadline_date": deadl,
                    "compliance_type": d.get('type', 'Document'),
                    "status": 'pending',
                    "urgency": d.get('urgency', 'medium'),
                    "source_document_id": mongo_doc_id,
                    "created_by_agent": "VEDA"
                }
                await db.execute(insert(ComplianceDeadline).values(**deadline_obj))
                new_deadlines.append(deadline_obj)
            except Exception as e:
                print(f"Date parsing error: {e}")

        await db.commit()
        return {"document_id": mongo_doc_id, "deadlines_found": len(new_deadlines), "data": data}
