
 ██ ▄█▀▄▄▄       ██▓███   ███▄    █ 
 ██▄█▒▒████▄    ▓██░  ██▒ ██ ▀█   █ 
▓███▄░▒██  ▀█▄  ▓██░ ██▓▒▓██  ▀█ ██▒
▓██ █▄░██▄▄▄▄██ ▒██▄█▓▒ ▒▓██▒  ▐▌██▒
▒██▒ █▄▓█   ▓██▒▒██▒ ░  ░▒██░   ▓██░
▒ ▒▒ ▓▒▒▒   ▓▒█░▒▓▒░ ░  ░░ ▒░   ▒ ▒ 
░ ░▒ ▒░ ▒   ▒▒ ░░▒ ░     ░ ░░   ░ ▒░
░ ░░ ░  ░   ▒   ░░          ░   ░ ░ 
░  ░        ░  ░                  ░ 
                                    


# kapn - Discord Chat AI Analyzer

A local web application that allows you to analyze Discord chat conversations using Google's Gemini AI. This tool fetches messages from a Discord channel, stores them in a local SQLite database, and provides AI-powered topic extraction and summarization.

## Features

- Fetch messages from Discord channels via the Discord API
- Store message history locally in SQLite database
- Extract main discussion topics using Google's Gemini AI
- Generate detailed summaries of specific conversation topics
- Clean, responsive UI built with Tailwind CSS

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file based on the provided `.env.example`
4. Run the application:
   ```
   python app.py
   ```
5. Access the web interface at `http://localhost:5000`

## Required Credentials

- **Discord Auth Token**: Your personal Discord authentication token
- **Server ID**: ID of the Discord server you want to analyze
- **Channel ID**: ID of the specific channel within the server
- **Google API Key**: A Google API key with access to the Gemini API

## Usage

1. Enter your credentials in the Configuration panel
2. Click "Save Config" to store credentials in your browser
3. Click "Check Status" to verify your credentials are valid
4. Click "Fetch Recent Messages" to download messages from Discord
5. Click "View Messages" to see the fetched messages
6. Click "Extract Topics" to generate topic categories from the conversation
7. Select a topic from the dropdown and click "Generate Summary" to get a detailed summary

## Security Notes

- All credentials are stored in your browser's localStorage and are never sent to any third-party servers
- Credentials are only used to directly access the Discord and Google APIs
- Messages are stored locally in a SQLite database on your machine
