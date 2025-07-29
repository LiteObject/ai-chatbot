#!/usr/bin/env python3
"""
OpenAI Pricing Updater

This script provides multiple methods to fetch current OpenAI pricing:
1. Web scraping from OpenAI's pricing page
2. External pricing APIs (when available)
3. Manual configuration file updates
4. Fallback to cached pricing data

Usage:
    python update_pricing.py --method web_scrape
    python update_pricing.py --method api
    python update_pricing.py --method manual
"""

import json
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import argparse
import sys
from datetime import datetime
import os
from pathlib import Path


class OpenAIPricingUpdater:
    """Updates OpenAI pricing from various sources."""

    def __init__(self):
        self.config_path = Path(__file__).parent / \
            "config" / "openai_pricing.json"
        self.token_tracker_path = Path(
            __file__).parent / "src" / "token_tracker.py"

    def fetch_pricing_web_scrape(self) -> Optional[Dict[str, Any]]:
        """
        Fetch pricing by scraping OpenAI's pricing page.
        Note: This is fragile and may break if OpenAI changes their page structure.
        """
        try:
            url = "https://openai.com/pricing"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # This is a simplified example - actual implementation would need
            # to parse the specific HTML structure of OpenAI's pricing page
            pricing_data = self._parse_pricing_from_html(soup)

            if pricing_data:
                pricing_data["last_updated"] = datetime.now().isoformat()
                pricing_data["source"] = "web_scrape"
                return pricing_data

        except Exception as e:
            print(f"Error scraping pricing: {e}")
            return None

    def _parse_pricing_from_html(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Parse pricing data from HTML soup.
        This would need to be updated based on OpenAI's actual page structure.
        """
        # Placeholder implementation - would need actual parsing logic
        # based on OpenAI's current HTML structure
        print("Web scraping parsing not fully implemented - requires specific HTML structure analysis")
        return None

    def fetch_pricing_external_api(self) -> Optional[Dict[str, Any]]:
        """
        Fetch pricing from external APIs that track OpenAI pricing.
        """
        # Example external APIs (these may not exist or be free):
        apis_to_try = [
            "https://api.openai-pricing.com/v1/pricing",  # Hypothetical
            "https://api.ai-pricing-tracker.com/openai",  # Hypothetical
        ]

        for api_url in apis_to_try:
            try:
                response = requests.get(api_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if self._validate_pricing_data(data):
                        data["last_updated"] = datetime.now().isoformat()
                        data["source"] = "external_api"
                        return data
            except Exception as e:
                print(f"Error fetching from {api_url}: {e}")
                continue

        print("No external API sources available")
        return None

    def fetch_pricing_github_repo(self) -> Optional[Dict[str, Any]]:
        """
        Fetch pricing from a community-maintained GitHub repository.
        """
        try:
            # Example: Community-maintained pricing data
            url = "https://raw.githubusercontent.com/community/openai-pricing/main/pricing.json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if self._validate_pricing_data(data):
                    data["last_updated"] = datetime.now().isoformat()
                    data["source"] = "github_community"
                    return data

        except Exception as e:
            print(f"Error fetching from GitHub: {e}")

        return None

    def _validate_pricing_data(self, data: Dict[str, Any]) -> bool:
        """Validate that pricing data has expected structure."""
        if not isinstance(data, dict):
            return False

        # Check for required models
        required_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]

        for model in required_models:
            if model not in data:
                return False
            if not isinstance(data[model], dict):
                return False
            if "input" not in data[model] or "output" not in data[model]:
                return False

        return True

    def load_current_pricing(self) -> Dict[str, Any]:
        """Load current pricing from config file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading current pricing: {e}")

        # Return fallback pricing
        return self._get_fallback_pricing()

    def save_pricing_config(self, pricing_data: Dict[str, Any]) -> bool:
        """Save pricing data to config file."""
        try:
            # Create config directory if it doesn't exist
            self.config_path.parent.mkdir(exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(pricing_data, f, indent=2)

            print(f"Pricing saved to {self.config_path}")
            return True

        except Exception as e:
            print(f"Error saving pricing config: {e}")
            return False

    def update_token_tracker(self, pricing_data: Dict[str, Any]) -> bool:
        """Update the token_tracker.py file with new pricing."""
        try:
            if not self.token_tracker_path.exists():
                print(
                    f"Token tracker file not found: {self.token_tracker_path}")
                return False

            # Read current file
            with open(self.token_tracker_path, 'r') as f:
                content = f.read()

            # Create new pricing dictionary string
            pricing_dict = self._format_pricing_dict(pricing_data)

            # Replace the OPENAI_PRICING dictionary
            import re
            pattern = r'OPENAI_PRICING\s*=\s*{[^}]*(?:{[^}]*}[^}]*)*}'

            if re.search(pattern, content, re.DOTALL):
                new_content = re.sub(
                    pattern,
                    f'OPENAI_PRICING = {pricing_dict}',
                    content,
                    flags=re.DOTALL
                )

                # Write updated content
                with open(self.token_tracker_path, 'w') as f:
                    f.write(new_content)

                print(f"Updated token_tracker.py with new pricing")
                return True
            else:
                print("Could not find OPENAI_PRICING dictionary in token_tracker.py")
                return False

        except Exception as e:
            print(f"Error updating token tracker: {e}")
            return False

    def _format_pricing_dict(self, pricing_data: Dict[str, Any]) -> str:
        """Format pricing data as Python dictionary string."""
        lines = ["{"]

        # Group models by type
        gpt4_models = {k: v for k, v in pricing_data.items()
                       if k.startswith("gpt-4")}
        gpt35_models = {k: v for k, v in pricing_data.items()
                        if k.startswith("gpt-3.5")}
        embedding_models = {k: v for k,
                            v in pricing_data.items() if "embedding" in k}

        if gpt4_models:
            lines.append("    # GPT-4 models")
            for model, prices in gpt4_models.items():
                lines.append(
                    f'    "{model}": {{"input": {prices["input"]}, "output": {prices["output"]}}},')
            lines.append("")

        if gpt35_models:
            lines.append("    # GPT-3.5 models")
            for model, prices in gpt35_models.items():
                lines.append(
                    f'    "{model}": {{"input": {prices["input"]}, "output": {prices["output"]}}},')
            lines.append("")

        if embedding_models:
            lines.append("    # Embedding models")
            for model, prices in embedding_models.items():
                lines.append(
                    f'    "{model}": {{"input": {prices["input"]}, "output": {prices["output"]}}},')

        lines.append("}")
        return "\n".join(lines)

    def _get_fallback_pricing(self) -> Dict[str, Any]:
        """Return fallback pricing data."""
        return {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-0125": {"input": 0.0005, "output": 0.0015},
            "gpt-3.5-turbo-instruct": {"input": 0.0015, "output": 0.002},
            "text-embedding-ada-002": {"input": 0.0001, "output": 0.0},
            "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
            "text-embedding-3-large": {"input": 0.00013, "output": 0.0},
            "last_updated": "2025-07-28",
            "source": "fallback"
        }

    def update_pricing(self, method: str = "auto") -> bool:
        """Update pricing using specified method."""
        print(f"Updating OpenAI pricing using method: {method}")

        pricing_data = None

        if method == "auto":
            # Try methods in order of preference
            methods = ["github", "external_api", "web_scrape"]
            for m in methods:
                print(f"Trying method: {m}")
                if m == "github":
                    pricing_data = self.fetch_pricing_github_repo()
                elif m == "external_api":
                    pricing_data = self.fetch_pricing_external_api()
                elif m == "web_scrape":
                    pricing_data = self.fetch_pricing_web_scrape()

                if pricing_data:
                    break

        elif method == "web_scrape":
            pricing_data = self.fetch_pricing_web_scrape()
        elif method == "external_api":
            pricing_data = self.fetch_pricing_external_api()
        elif method == "github":
            pricing_data = self.fetch_pricing_github_repo()
        elif method == "manual":
            print("Manual update mode - please edit config/openai_pricing.json manually")
            return True

        if pricing_data:
            # Save to config file
            if self.save_pricing_config(pricing_data):
                # Update token tracker
                if self.update_token_tracker(pricing_data):
                    print("✅ Pricing updated successfully!")
                    return True
                else:
                    print(
                        "⚠️ Pricing saved to config but failed to update token_tracker.py")
                    return False
            else:
                print("❌ Failed to save pricing data")
                return False
        else:
            print("❌ Could not fetch pricing data from any source")
            print("💡 Consider using fallback pricing or manual update")
            return False


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Update OpenAI pricing data")
    parser.add_argument(
        "--method",
        choices=["auto", "web_scrape", "external_api", "github", "manual"],
        default="auto",
        help="Method to use for fetching pricing"
    )
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Only update config file, not token_tracker.py"
    )

    args = parser.parse_args()

    updater = OpenAIPricingUpdater()

    if args.method == "manual":
        print("Manual update instructions:")
        print("1. Edit config/openai_pricing.json with current pricing")
        print("2. Run this script again with --method=manual to apply changes")

        # Create example config if it doesn't exist
        if not updater.config_path.exists():
            example_config = updater._get_fallback_pricing()
            updater.save_pricing_config(example_config)
            print(f"Created example config at {updater.config_path}")
    else:
        success = updater.update_pricing(args.method)
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
