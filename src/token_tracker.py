"""
Token tracking and cost calculation utilities for OpenAI API usage.
"""
import tiktoken
from typing import Dict, Any, Tuple
from datetime import datetime
import streamlit as st
import json
import os
from pathlib import Path


def load_pricing_config() -> Dict[str, Dict[str, float]]:
    """Load pricing configuration from file, with fallback to hardcoded values."""
    config_path = Path(__file__).parent.parent / \
        "config" / "openai_pricing.json"

    try:
        if config_path.exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                # Remove metadata fields, keep only pricing data
                pricing = {k: v for k, v in data.items()
                           if isinstance(v, dict) and "input" in v and "output" in v}
                if pricing:
                    return pricing
    except Exception as e:
        print(f"Warning: Could not load pricing config: {e}")

    # Fallback to hardcoded pricing
    return get_fallback_pricing()


def get_fallback_pricing() -> Dict[str, Dict[str, float]]:
    """Get fallback hardcoded pricing (as of July 2025)."""
    return {
        # GPT-4 models
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},

        # GPT-3.5 models
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
        "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002},

        # Embedding models
        "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},
        "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
    }


# Load pricing at module level (will be refreshed when module is reloaded)
OPENAI_PRICING = load_pricing_config()


class TokenTracker:
    """Tracks token usage and calculates costs for OpenAI API calls."""

    def __init__(self):
        """Initialize the token tracker."""
        self.initialize_session_state()
        self._pricing_cache = None
        self._pricing_last_loaded = None

    def refresh_pricing(self) -> bool:
        """Refresh pricing data from configuration file."""
        try:
            global OPENAI_PRICING
            new_pricing = load_pricing_config()
            OPENAI_PRICING = new_pricing
            self._pricing_cache = new_pricing
            self._pricing_last_loaded = datetime.now()
            return True
        except Exception as e:
            print(f"Error refreshing pricing: {e}")
            return False

    def get_pricing_info(self) -> Dict[str, Any]:
        """Get information about current pricing data."""
        config_path = Path(__file__).parent.parent / \
            "config" / "openai_pricing.json"

        info = {
            "pricing_source": "hardcoded_fallback",
            "last_updated": "unknown",
            "config_file_exists": config_path.exists(),
            "models_count": len(OPENAI_PRICING)
        }

        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    info["pricing_source"] = data.get("source", "config_file")
                    info["last_updated"] = data.get("last_updated", "unknown")
        except Exception:
            pass

        return info

    def initialize_session_state(self):
        """Initialize session state for token tracking."""
        if "token_usage" not in st.session_state:
            st.session_state.token_usage = {
                "total_tokens": 0,
                "total_cost": 0.0,
                "session_tokens": 0,
                "session_cost": 0.0,
                "requests": []
            }

    def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Count tokens in text using tiktoken."""
        try:
            # Map model names to tiktoken encodings
            encoding_map = {
                "gpt-4": "cl100k_base",
                "gpt-4-turbo": "cl100k_base",
                "gpt-4-turbo-preview": "cl100k_base",
                "gpt-4o": "cl100k_base",
                "gpt-4o-mini": "cl100k_base",
                "gpt-3.5-turbo": "cl100k_base",
                "gpt-3.5-turbo-0125": "cl100k_base",
                "gpt-3.5-turbo-instruct": "cl100k_base",
                "text-embedding-ada-002": "cl100k_base",
                "text-embedding-3-small": "cl100k_base",
                "text-embedding-3-large": "cl100k_base",
            }

            encoding_name = encoding_map.get(model, "cl100k_base")
            encoding = tiktoken.get_encoding(encoding_name)
            return len(encoding.encode(text))

        except Exception:
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4

    def calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost for token usage."""
        if model not in OPENAI_PRICING:
            # Use gpt-3.5-turbo as default
            model = "gpt-3.5-turbo"

        pricing = OPENAI_PRICING[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]

        return input_cost + output_cost

    def track_request(self,
                      input_text: str,
                      output_text: str,
                      model: str,
                      request_type: str = "chat") -> Dict[str, Any]:
        """Track a single API request and return usage info."""
        input_tokens = self.count_tokens(input_text, model)
        output_tokens = self.count_tokens(output_text, model)
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(input_tokens, output_tokens, model)

        # Create request record
        request_info = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "type": request_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": cost
        }

        # Update session state
        st.session_state.token_usage["total_tokens"] += total_tokens
        st.session_state.token_usage["total_cost"] += cost
        st.session_state.token_usage["session_tokens"] += total_tokens
        st.session_state.token_usage["session_cost"] += cost
        st.session_state.token_usage["requests"].append(request_info)

        # Keep only last 100 requests to avoid memory issues
        if len(st.session_state.token_usage["requests"]) > 100:
            st.session_state.token_usage["requests"] = st.session_state.token_usage["requests"][-100:]

        return request_info

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session usage."""
        return {
            "session_tokens": st.session_state.token_usage["session_tokens"],
            "session_cost": st.session_state.token_usage["session_cost"],
            "total_tokens": st.session_state.token_usage["total_tokens"],
            "total_cost": st.session_state.token_usage["total_cost"],
            "request_count": len(st.session_state.token_usage["requests"])
        }

    def reset_session_usage(self):
        """Reset session usage counters."""
        st.session_state.token_usage["session_tokens"] = 0
        st.session_state.token_usage["session_cost"] = 0.0

    def format_cost(self, cost: float) -> str:
        """Format cost for display."""
        if cost < 0.01:
            return f"${cost:.4f}"
        else:
            return f"${cost:.3f}"

    def format_tokens(self, tokens: int) -> str:
        """Format token count for display."""
        if tokens >= 1000:
            return f"{tokens:,}"
        else:
            return str(tokens)


# Global token tracker instance
token_tracker = TokenTracker()


def estimate_embedding_tokens(text: str) -> Tuple[int, float]:
    """Estimate tokens and cost for embedding generation."""
    tokens = token_tracker.count_tokens(text, "text-embedding-ada-002")
    cost = token_tracker.calculate_cost(tokens, 0, "text-embedding-ada-002")
    return tokens, cost


def create_usage_display(request_info: Dict[str, Any]) -> str:
    """Create a formatted usage display string."""
    model = request_info["model"]
    tokens = request_info["total_tokens"]
    cost = request_info["cost"]

    return f"🔢 **{token_tracker.format_tokens(tokens)} tokens** ({model}) • 💰 **{token_tracker.format_cost(cost)}**"
