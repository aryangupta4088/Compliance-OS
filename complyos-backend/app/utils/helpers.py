from datetime import datetime, timedelta
from typing import Optional, Dict
import json
import uuid
import re

def parse_date_string(date_str: str) -> Optional[datetime]:
    """Attempts to parse date string in multiple formats"""
    formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def calculate_urgency(deadline_date: datetime) -> str:
    """Calculates urgency based on days remaining"""
    days_left = (deadline_date - datetime.utcnow()).days
    if days_left < 3:
        return "high"
    elif days_left < 7:
        return "medium"
    return "low"

def sanitize_json_response(text: str) -> Optional[Dict]:
    """Strips markdown and extracts JSON"""
    try:
        # Remove markdown backticks
        clean_text = re.sub(r"```(?:json)?\n?|```", "", text).strip()
        return json.loads(clean_text)
    except Exception:
        return None

def generate_session_id() -> str:
    """Generates a unique session ID"""
    return str(uuid.uuid4())
