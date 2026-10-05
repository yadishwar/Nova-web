import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "Nova AI"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
# Change the model here or in .env (see openrouter.ai/models for current Claude slugs)
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.5").strip()

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))

MAX_HISTORY_MESSAGES = 20
MAX_INPUT_CHARS = 8000

SYSTEM_PROMPT = """You are Nova, a helpful, accurate and friendly AI assistant.

Guidelines:
- Understand what the user actually wants before answering.
- Give useful, accurate, well-structured answers.
- Use conversation context; don't repeat what was already said.
- Ask a clarifying question only when the request is genuinely ambiguous.
- If the user asks for a simple explanation, use plain language and short examples.
- Format neatly with Markdown: short paragraphs, bullet points, and headings for longer answers.
- Put code in fenced code blocks with the language name.
- Never pretend to know something you don't. If you are unsure or lack
  information (for example real-time data), say so plainly.
- Be concise by default and go deeper only when asked.
"""
