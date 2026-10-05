import requests

from config import (
    MAX_HISTORY_MESSAGES,
    MAX_TOKENS,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
    OPENROUTER_URL,
    REQUEST_TIMEOUT,
    SYSTEM_PROMPT,
    TEMPERATURE,
)


class OpenRouterError(Exception):
    """A user-friendly error message plus the HTTP status to return."""

    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status


STATUS_MESSAGES = {
    400: "The request was rejected. Try rephrasing or shortening your message.",
    401: "Your API key is invalid. Check OPENROUTER_API_KEY in your .env file.",
    402: "Your OpenRouter account is out of credits. Add credits at openrouter.ai.",
    403: "This request was blocked by the provider's moderation.",
    404: "Model not found. Check OPENROUTER_MODEL in your .env file.",
    408: "The request timed out. Please try again.",
    429: "Too many requests. Please wait a moment and try again.",
    500: "OpenRouter had an internal error. Please try again.",
    502: "The model provider is unavailable right now. Please try again.",
    503: "No provider is available for this model right now. Please try again.",
}


def _error_from_response(response):
    message = STATUS_MESSAGES.get(response.status_code)
    if message:
        return message
    try:
        detail = response.json().get("error", {}).get("message", "")
    except ValueError:
        detail = ""
    return f"Unexpected error ({response.status_code}). {detail}".strip()


def ask_claude(history):
    """Send the conversation to Claude via OpenRouter and return the reply text."""
    if not OPENROUTER_API_KEY:
        raise OpenRouterError(
            "Server has no API key. Add OPENROUTER_API_KEY to .env and restart.", 500
        )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Nova AI",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
        + history[-MAX_HISTORY_MESSAGES:],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    try:
        response = requests.post(
            OPENROUTER_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
        )
    except requests.exceptions.Timeout:
        raise OpenRouterError("The request timed out. Please try again.", 504)
    except requests.exceptions.ConnectionError:
        raise OpenRouterError("Couldn't reach OpenRouter. Check the server's internet.", 502)
    except requests.exceptions.RequestException as exc:
        raise OpenRouterError(f"Network error: {exc}", 502)

    if response.status_code != 200:
        raise OpenRouterError(_error_from_response(response), 502)

    try:
        data = response.json()
    except ValueError:
        raise OpenRouterError("Received an invalid response from OpenRouter.", 502)

    if isinstance(data, dict) and data.get("error"):
        detail = data["error"].get("message", "Unknown error")
        raise OpenRouterError(f"OpenRouter error: {detail}", 502)

    choices = data.get("choices") or []
    if not choices:
        raise OpenRouterError("The model returned no response. Please try again.", 502)

    content = (choices[0].get("message") or {}).get("content")
    if not content or not content.strip():
        raise OpenRouterError("The model returned an empty response. Please try again.", 502)

    return content.strip()
