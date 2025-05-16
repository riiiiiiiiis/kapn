"""Discord message scraper module to fetch messages from Discord API."""

import os
import time
import datetime
import requests
from typing import List, Dict, Any, Optional
from database import db


def timestamp_to_snowflake(timestamp_ms: int) -> str:
    return str((timestamp_ms - 1420070400000) << 22)


def iso_to_unix_ms(iso_timestamp: str) -> int:
    dt = datetime.datetime.fromisoformat(iso_timestamp.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)


class DiscordScraper:
    def __init__(self, auth_token: str, server_id: str, channel_id: str):
        self.auth_token = auth_token
        self.server_id = server_id
        self.channel_id = channel_id
        self.api_base = "https://discord.com/api/v10"
        self.headers = {
            "Authorization": auth_token,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

    def validate_token(self) -> bool:
        try:
            resp = requests.get(f"{self.api_base}/users/@me", headers=self.headers, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def fetch_messages(self, hours_ago: int = 24) -> List[Dict[str, Any]]:
        timestamp_24h_ago = int(time.time() * 1000) - (hours_ago * 60 * 60 * 1000)
        snowflake_24h_ago = timestamp_to_snowflake(timestamp_24h_ago)
        
        all_messages = []
        endpoint = f"{self.api_base}/channels/{self.channel_id}/messages"
        params = {"after": snowflake_24h_ago, "limit": 100}
        
        while True:
            try:
                response = requests.get(endpoint, headers=self.headers, params=params, timeout=15)
                
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 5))
                    time.sleep(retry_after + 0.5)
                    continue
                    
                if response.status_code != 200:
                    break
                
                messages_batch = response.json()
                if not messages_batch:
                    break
                
                rate_limit_remaining = int(response.headers.get("X-RateLimit-Remaining", "5"))
                rate_limit_reset = float(response.headers.get("X-RateLimit-Reset-After", "0"))
                
                if rate_limit_remaining <= 1:
                    time.sleep(rate_limit_reset + 0.5)
                
                if not messages_batch:
                    break
                
                for msg in messages_batch:
                    processed_msg = {
                        "message_id": msg.get("id", ""),
                        "channel_id": self.channel_id,
                        "server_id": self.server_id,
                        "author_id": msg.get("author", {}).get("id", ""),
                        "author_name": msg.get("author", {}).get("username", ""),
                        "content": msg.get("content", ""),
                        "timestamp": iso_to_unix_ms(msg.get("timestamp", "")),
                        "edited_ts": iso_to_unix_ms(msg.get("edited_timestamp", "")) if msg.get("edited_timestamp") else None
                    }
                    all_messages.append(processed_msg)
                
                params["after"] = messages_batch[-1]["id"]
                
            except Exception as e:
                break
                
        db.insert_messages(all_messages)
        return all_messages

    def fetch_and_store_messages(self) -> int:
        messages = self.fetch_messages()
        return len(messages)
