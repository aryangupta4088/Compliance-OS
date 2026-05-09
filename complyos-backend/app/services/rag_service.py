import json
import asyncio
from typing import List
# Mock embedding for simplicity in POC, real would use sentence-transformers
# from sentence_transformers import SentenceTransformer

class RAGService:
    def __init__(self):
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')
        pass

    async def get_scheme_context(self, query: str, top_k: int = 10) -> List[str]:
        """
        Mock similarity search. In production, this would query pgvector.
        """
        # For POC, we just return all seeded schemes if query matches partially
        from app.database import mongo_db
        cursor = mongo_db.schemes_kb.find({})
        docs = await cursor.to_list(length=top_k)
        return [doc['text'] for doc in docs]

    async def add_scheme_to_kb(self, scheme_text: str):
        """Embeds and inserts into KB (using MongoDB for POC)"""
        from app.database import mongo_db
        await mongo_db.schemes_kb.insert_one({"text": scheme_text, "timestamp": "now"})

async def seed_schemes():
    """Seeds the KB with 16 core schemes"""
    schemes = [
        "PM SVANidhi: Micro-credit facility for street vendors.",
        "MUDRA Shishu: Loans up to Rs. 50,000 for startups.",
        "MUDRA Kishore: Loans from Rs. 50,001 to Rs. 5 Lakh.",
        "MUDRA Tarun: Loans from Rs. 5,00,001 to Rs. 10 Lakh.",
        "CGTMSE: Credit Guarantee Fund Trust for Micro and Small Enterprises.",
        "Stand Up India: Loans for SC/ST and Women entrepreneurs.",
        "Udyogini: Scheme for Women Entrepreneurs by Karnataka/Govt.",
        "Mahila Udyam Nidhi: Equity assistance for women units.",
        "PMEGP: Prime Minister's Employment Generation Programme.",
        "ZED Certification: Zero Defect Zero Effect manufacturing.",
        "CLCSS: Credit Linked Capital Subsidy Scheme for Tech Upgradation.",
        "NSIC: National Small Industries Corporation schemes.",
        "GeM: Government e-Marketplace for MSME procurement.",
        "Startup India: Tax exemptions and support for innovative startups.",
        "One District One Product: Supporting traditional industrial clusters.",
        "PM Vishwakarma: Support for traditional artisans and craftspeople."
    ]
    rag = RAGService()
    for s in schemes:
        await rag.add_scheme_to_kb(s)
    print("Successfully seeded 16 schemes.")

if __name__ == "__main__":
    asyncio.run(seed_schemes())
