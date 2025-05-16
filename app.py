"""Main Flask application for Discord Chat Analyzer."""

import os
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, List
from functools import wraps
from flask import Flask, render_template, request, jsonify

from dotenv import load_dotenv
import requests

from database import db
from scraper import DiscordScraper
from analyzer import MessageAnalyzer

load_dotenv()

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=2)

def json_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return jsonify(result)
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    return wrapper

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check_status", methods=["POST"])
@json_response
def check_status():
    data = request.get_json()
    
    discord_token = data.get("discord_token", "")
    gemini_key = data.get("gemini_key", "")
    server_id = data.get("server_id", "")
    channel_id = data.get("channel_id", "")
    
    # Validate inputs
    if not all([discord_token, gemini_key, server_id, channel_id]):
        return {
            "status": "error", 
            "message": "All fields are required",
            "discord_ok": False,
            "gemini_ok": False
        }
    
    # Check Discord token
    discord_ok = False
    try:
        scraper = DiscordScraper(discord_token, server_id, channel_id)
        discord_ok = scraper.validate_token()
    except Exception:
        discord_ok = False
    
    # Check Gemini key
    gemini_ok = False
    try:
        analyzer = MessageAnalyzer(gemini_key)
        gemini_ok = analyzer.validate_key()
    except Exception:
        gemini_ok = False
    
    return {
        "status": "success" if discord_ok and gemini_ok else "error",
        "discord_ok": discord_ok, 
        "gemini_ok": gemini_ok,
        "message": "Configuration validated successfully" if discord_ok and gemini_ok else "One or more configurations are invalid"
    }

@app.route("/fetch_messages", methods=["POST"])
@json_response
def fetch_messages():
    data = request.get_json()
    
    discord_token = data.get("discord_token", "")
    server_id = data.get("server_id", "")
    channel_id = data.get("channel_id", "")
    
    if not all([discord_token, server_id, channel_id]):
        return {"status": "error", "message": "Missing required fields"}
    
    def fetch_task():
        try:
            scraper = DiscordScraper(discord_token, server_id, channel_id)
            scraper.fetch_messages()
        except Exception as e:
            print(f"Error fetching messages: {e}")
    
    executor.submit(fetch_task)
    
    return {
        "status": "scraping_initiated", 
        "message": "Message fetching started. Please refresh messages after a short while."
    }

@app.route("/get_displayed_messages", methods=["POST"])
@json_response
def get_displayed_messages():
    data = request.get_json()
    
    server_id = data.get("server_id", "")
    channel_id = data.get("channel_id", "")
    
    if not all([server_id, channel_id]):
        return {"status": "error", "message": "Missing required fields"}
    
    # Get last 24 hours of messages
    one_day_ago_ms = int(time.time() * 1000) - (24 * 60 * 60 * 1000)
    messages = db.get_recent_messages(channel_id, one_day_ago_ms)
    
    return {
        "status": "success",
        "messages": messages
    }

@app.route("/get_topics", methods=["POST"])
@json_response
def get_topics():
    data = request.get_json()
    
    server_id = data.get("server_id", "")
    channel_id = data.get("channel_id", "")
    gemini_key = data.get("gemini_key", "")
    
    if not all([server_id, channel_id, gemini_key]):
        return {"status": "error", "message": "Missing required fields"}
    
    # Get messages from the last 24 hours
    one_day_ago_ms = int(time.time() * 1000) - (24 * 60 * 60 * 1000)
    messages = db.get_recent_messages(channel_id, one_day_ago_ms)
    
    if not messages:
        return {"status": "error", "message": "No messages found for analysis"}
    
    analyzer = MessageAnalyzer(gemini_key)
    chat_log = analyzer.format_messages_for_analysis(messages)
    topics = analyzer.extract_topics(chat_log)
    
    return {
        "status": "success",
        "topics": topics
    }

@app.route("/get_summary", methods=["POST"])
@json_response
def get_summary():
    data = request.get_json()
    
    server_id = data.get("server_id", "")
    channel_id = data.get("channel_id", "")
    gemini_key = data.get("gemini_key", "")
    topic = data.get("topic", "")
    
    if not all([server_id, channel_id, gemini_key, topic]):
        return {"status": "error", "message": "Missing required fields"}
    
    # Get messages from the last 24 hours
    one_day_ago_ms = int(time.time() * 1000) - (24 * 60 * 60 * 1000)
    messages = db.get_recent_messages(channel_id, one_day_ago_ms)
    
    if not messages:
        return {"status": "error", "message": "No messages found for analysis"}
    
    analyzer = MessageAnalyzer(gemini_key)
    chat_log = analyzer.format_messages_for_analysis(messages)
    summary = analyzer.summarize_topic(chat_log, topic)
    
    return {
        "status": "success",
        "summary": summary
    }

def find_available_port(start_port=5000, max_attempts=100):
    """Find an available port starting from start_port."""
    import socket
    
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts - 1}")

if __name__ == "__main__":
    port = find_available_port(5000)
    print(f"Starting server on port {port}")
    app.run(debug=True, host="0.0.0.0", port=port)
