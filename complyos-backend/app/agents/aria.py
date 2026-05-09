import json
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from app.config import settings

ARIA_SYSTEM_PROMPT = """
You are ARIA, a friendly compliance assistant for Indian small business owners on ComplianceOS.
Speak in simple Hindi or English based on user preference.
Ask ONE question at a time. Never overwhelm the user.
Be warm, encouraging, use simple words — no legal jargon.

Collect this information one by one:
1. Business name and type (shop/factory/service/food/other)
2. Location — state and district
3. Business size — employees and yearly turnover range
4. Existing registrations (GST/Udyam/Shop License/PAN/other)
5. Gender of owner (for women-specific scheme benefits)
6. Any government schemes already enrolled in

Rules:
- If user mentions a scheme name, note it as already enrolled
- Explain why you are asking each question in one simple line
- When all info is collected say exactly: "Profile complete!"
  then give a warm summary of what you learned
- If user asks anything off-topic, answer briefly then return to onboarding
"""

PROFILE_EXTRACTION_PROMPT = """
Extract a structured business profile from this conversation.
Return ONLY valid JSON. No explanation. No markdown.

Conversation:
{conversation_history}

Return this exact JSON structure:
{{
  "business_name": "",
  "business_type": "",
  "sector": "",
  "state": "",
  "district": "",
  "turnover_range": "",
  "employee_count": "",
  "is_women_led": false,
  "existing_registrations": [],
  "enrolled_schemes": [],
  "preferred_language": "en"
}}
"""

class ARIAAgent:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=0,
            streaming=True
        )
        self.memory = ConversationBufferWindowMemory(k=10, return_messages=True)
        self.chain = ConversationChain(
            llm=self.llm,
            memory=self.memory,
            verbose=False
        )

    async def process_message(self, user_input: str):
        response_text = ""

        async for chunk in self.chain.astream({"input": user_input}):
            if isinstance(chunk, str):
                response_text += chunk
                yield {"type": "token", "content": chunk}
            elif hasattr(chunk, 'content'):
                response_text += chunk.content
                yield {"type": "token", "content": chunk.content}

        if "Profile complete!" in response_text:
            extraction_llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model_name=settings.GROQ_MODEL,
                temperature=0
            )

            history = self.memory.chat_memory.messages
            context_str = "\n".join([f"{m.type}: {m.content}" for m in history])

            extraction_response = await extraction_llm.ainvoke([
                ("system", PROFILE_EXTRACTION_PROMPT.format(conversation_history=context_str)),
                ("user", "Extract now.")
            ])

            try:
                json_data = json.loads(extraction_response.content)
                yield {"type": "profile_complete", "data": json_data}
                self.clear_memory()
            except json.JSONDecodeError:
                yield {"type": "error", "message": "Failed to parse profile data"}

    def clear_memory(self):
        self.memory.clear()