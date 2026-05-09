import json
import httpx
from langchain_groq import ChatGroq
from app.config import settings
from app.database import mongo_db, redis_client

MONITORED_SOURCES = [
  "https://cbic-gst.gov.in",
  "https://mca.gov.in",
  "https://labour.gov.in"
]

SENTINEL_PROMPT = """
You are SENTINEL, a regulatory monitoring agent.
Analyze this circular. Return ONLY valid JSON.

{{
  "plain_language_summary": "...",
  "affected_business_types": [],
  "affected_states": ["All India"],
  "action_required": "...",
  "urgency": "high/medium/low",
  "compliance_area": "GST/Labour/MCA"
}}

Circular: {text}
Source: {source}
"""

class SentinelAgent:
    def __init__(self):
        self.llm = ChatGroq(groq_api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL, temperature=0)
        self.client = httpx.AsyncClient(timeout=10.0)

    async def monitor_sources(self):
        findings = []
        for url in MONITORED_SOURCES:
            # Strict .gov.in check handled implicitly by list usage
            try:
                resp = await self.client.get(url)
                # Logic here would parse RSS/HTML for changes vs last check hash
                # For POC, assume we find 'New Circular Text' somehow
                # fake_text = "The GST Council has announced changes to filing..."
                # analysis = await self.analyze(fake_text, url)
                # findings.append(analysis)
                pass 
            except Exception as e:
                print(f"Sentinel Error fetching {url}: {e}")
        
        return findings

    async def analyze_circular(self, text: str, source: str):
        response = await self.llm.ainvoke([
            ("system", "You are a regulatory analyst."),
            ("user", SENTINEL_PROMPT.format(text=text, source=source))
        ])
        try:
            data = json.loads(response.content)
            # Save to MongoDB Audit Log
            await mongo_db.regulatory_changes.insert_one({
                "analysis": data, "source": source, "timestamp": "now"
            })
            return data
        except:
            return None
