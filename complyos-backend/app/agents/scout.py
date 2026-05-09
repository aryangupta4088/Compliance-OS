import json
from langchain_groq import ChatGroq
from app.config import settings

SCOUT_PROMPT = """
You are SCOUT, a government scheme discovery agent.

Business profile:
{business_profile}

Already enrolled — DO NOT recommend:
{enrolled_schemes}

Relevant schemes from knowledge base:
{context}

For each applicable scheme return JSON array:
[{{
  "scheme_name": "",
  "ministry": "",
  "scheme_type": "subsidy/loan/grant/training/equipment",
  "max_benefit": "",
  "eligibility_match_score": (0-100),
  "why_eligible": "one line plain language",
  "required_documents": [],
  "application_portal": "",
  "is_women_specific": boolean,
  "deadline": ""
}}]

Sort by eligibility_match_score descending. Return array only.
"""

class ScoutAgent:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0
        )
        # In a real app, load sentence_transformer model here
        # self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    async def find_schemes(self, profile: dict, enrolled: list, context_documents: list):
        # Context documents would come from pgvector similarity search
        context_text = "\n".join(context_documents) 
        
        response = await self.llm.ainvoke([
            ("system", "You are an expert on Indian Government schemes."),
            ("user", SCOUT_PROMPT.format(
                business_profile=json.dumps(profile, indent=2),
                enrolled_schemes=", ".join(enrolled),
                context=context_text
            ))
        ])
        
        try:
            return json.loads(response.content)
        except:
            return []
