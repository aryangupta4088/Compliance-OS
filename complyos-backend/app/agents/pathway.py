import json
from langchain_groq import ChatGroq
from app.config import settings

PORTAL_MAP = {
  "udyam": "https://udyamregistration.gov.in",
  "gst": "https://gst.gov.in",
  "mca": "https://mca.gov.in",
  "epfo": "https://epfindia.gov.in",
  "gem": "https://gem.gov.in"
}

PATHWAY_PROMPT = """
You are PATHWAY, a government registration assistant.
Business profile: {profile}
Completed: {completed}

Return JSON array of ALL needed registrations:
[{{
  "registration_name": "",
  "portal_url": "",
  "status": "completed/pending/not_started",
  "priority": "mandatory/recommended/optional",
  "why_needed": "",
  "steps": ["Step 1..."]
}}]

Sort mandatory first.
"""

class PathwayAgent:
    def __init__(self):
        self.llm = ChatGroq(groq_api_key=settings.GROQ_API_KEY, model_name=settings.GROQ_MODEL, temperature=0)

    async def generate_roadmap(self, profile: dict, existing_regs: list):
        response = await self.llm.ainvoke([
            ("system", "You are a registration expert."),
            ("user", PATHWAY_PROMPT.format(
                profile=json.dumps(profile),
                completed=", ".join(existing_regs)
            ))
        ])
        try:
            return json.loads(response.content)
        except:
            return []

    @staticmethod
    def schedule_submission(portal_name: str, form_data: dict, user_id: str):
        # Store in Redis Queue for Celery worker at 2 AM IST
        import asyncio
        from app.database import redis_client
        key = f"portal_queue:{user_id}:{portal_name}"
        loop = asyncio.get_event_loop()
        loop.run_until_complete(redis_client.set(key, json.dumps(form_data)))
        return True
