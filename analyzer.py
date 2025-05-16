"""Discord messages analyzer module using Google's Gemini API."""

import os
import datetime
from typing import List, Dict, Any, Optional
import google.generativeai as genai


class MessageAnalyzer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def validate_key(self) -> bool:
        try:
            response = self.model.generate_content("Hello")
            return response is not None
        except Exception:
            return False

    def format_messages_for_analysis(self, messages: List[Dict[str, Any]]) -> str:
        formatted_messages = []
        
        for msg in messages:
            timestamp_ms = msg.get("timestamp")
            if timestamp_ms:
                dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000)
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                
                author = msg.get("author_name", "Unknown User")
                content = msg.get("content", "")
                
                if content:  # Skip empty messages
                    formatted_messages.append(f"[{time_str}] {author}: {content}")
        
        return "\n".join(formatted_messages)

    def extract_topics(self, chat_log_string: str) -> List[str]:
        if not chat_log_string:
            return []
            
        prompt = f"""
Analyze the following Discord chat log and identify up to 5-7 main distinct topics of discussion.
List each main topic as a concise title (3-7 words).
Focus on significant themes and avoid overly granular or single-message topics.
If multiple discussions lead to a similar theme, consolidate them under one representative topic title.

Chat Log:
---
{chat_log_string}
---

Main Topics (numbered list):
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            topics = []
            for line in response_text.strip().split("\n"):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                    topic = line.lstrip("0123456789.- *").strip()
                    topics.append(topic)
            
            return topics[:7]  # Ensure max 7 topics
        except Exception:
            return []

    def summarize_topic(self, chat_log_string: str, topic: str) -> str:
        if not chat_log_string or not topic:
            return "No discussion data available for this topic."
            
        prompt = f"""
Topic to Summarize: "{topic}"

Chat Log Context:
---
{chat_log_string}
---

Provide a concise summary of the discussion specifically related to the topic: "{topic}".
Your summary must attribute key statements, opinions, questions, and decisions to the users who made them.
Use the format: "[username · HH:MM from original timestamp] specific_statement_or_point_summary."
Focus only on information and discussions directly relevant to the provided topic from the chat log context.
If the topic is not substantially discussed, clearly state that.
Organize the summary logically.
"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception:
            return "Failed to generate summary for this topic."
