"""
OpenAI Translation Provider.

Moved from providers/openai_provider.py to infrastructure layer.
"""

import os
import string
from typing import Dict, List
from .base import TranslationProvider
from ..logging import get_logger


class OpenAIProvider(TranslationProvider):
    """OpenAI-based translation provider."""
    
    def __init__(self):
        """Initialize OpenAI provider with API credentials."""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY missing")
        try:
            import openai  # noqa: F401
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                self.modern = True
            except Exception:
                self.client = None
                self.modern = False
        except Exception as e:
            raise RuntimeError("openai package not installed. pip install openai") from e
        self.logger = get_logger("newtone_translate")

    def translate_segments(self, segments: List[Dict], target_lang: str, source_lang: str,
                          brand_guide: Dict, glossary: Dict[str, str]):
        """Translate segments using OpenAI API."""
        import json as _json
        
        def is_only_punctuation(text):
            return all(char in string.punctuation or char.isspace() for char in text) and text.strip() != ""

        # Separate punctuation-only and translatable segments
        punctuation_segments = {}
        translatable_segments = []
        for seg in segments:
            if is_only_punctuation(seg["text"]):
                punctuation_segments[seg["id"]] = seg["text"]
            else:
                translatable_segments.append(seg)
        self.logger.info(f"Separated {len(punctuation_segments)} punctuation-only segments and {len(translatable_segments)} translatable segments.")

        # System prompt with explicit JSON instructions and placeholder preservation
        system = (
            "You are a senior luxury fashion copy translator. "
            "Translate the provided segments into the target language. "
            "Preserve placeholders like ⟦PH_n⟧ exactly. "
            "Do not add or remove content. "
            "Return ONLY valid JSON matching this schema (the word JSON must appear in your response):\n"
            "{\n"
            '  "translations": [ {"id": "<segment id>", "text": "<translation>"}... ],\n'
            '  "detected_language": "<iso>"\n'
            "}\n"
            "Every input segment id must appear exactly once in translations."
        )

        payload = {
            "source_lang": source_lang or "auto",
            "target_lang": target_lang,
            "brand": brand_guide or {},
            "glossary": glossary or {},
            "segments": [
                {"id": seg["id"], "text": seg["text"]}
                for seg in translatable_segments
            ],
            "segment_ids": [s["id"] for s in translatable_segments],
            "rules": {"preserve_placeholders": True},
        }
        user = _json.dumps(payload, ensure_ascii=False)
        self.logger.info(f"System prompt sent to AI: {system}")
        self.logger.info(f"Payload sent to AI: {user}")

        content = None
        usage = {"input": 0, "output": 0}
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Try with response_format first, then fallback if 400 error
        if getattr(self, "client", None) and getattr(self, "modern", False) and translatable_segments:
            try:
                resp = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"},
                )
                content = resp.choices[0].message.content
                usage = {
                    "input": getattr(resp.usage, "prompt_tokens", 0),
                    "output": getattr(resp.usage, "completion_tokens", 0),
                }
                self.logger.info(f"AI response content: {content}")
                self.logger.info(f"AI usage: {usage}")
            except Exception as e:
                self.logger.error(f"OpenAI API call with response_format failed: {e}")
                # Retry without response_format
                try:
                    resp = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system},
                            {"role": "user", "content": user},
                        ],
                        temperature=0.2
                    )
                    content = resp.choices[0].message.content
                    usage = {
                        "input": getattr(resp.usage, "prompt_tokens", 0),
                        "output": getattr(resp.usage, "completion_tokens", 0),
                    }
                    self.logger.info(f"AI response content (retry): {content}")
                    self.logger.info(f"AI usage (retry): {usage}")
                except Exception as e2:
                    self.logger.error(f"OpenAI API call without response_format also failed: {e2}")
                    content = '{"translations": [], "detected_language":"auto"}'
        else:
            content = '{"translations": [], "detected_language":"auto"}'
            self.logger.info("No translatable segments or OpenAI client unavailable. Returning default empty response.")

        # Robust JSON handling
        data = None
        try:
            data = _json.loads(content)
        except Exception as e:
            self.logger.error(f"Initial JSON parse failed: {e}. Attempting to extract JSON substring.")
            import re as _re
            match = _re.search(r'\{.*\}', content, _re.DOTALL)
            if match:
                try:
                    data = _json.loads(match.group(0))
                except Exception as e2:
                    self.logger.error(f"Secondary JSON parse failed: {e2}")
                    data = {"translations": [], "detected_language": "auto"}
            else:
                self.logger.error("No JSON object found in response.")
                data = {"translations": [], "detected_language": "auto"}

        trans_list = data.get("translations", [])
        detected = data.get("detected_language", "auto")
        mapping = {t["id"]: t["text"] for t in trans_list if "id" in t and "text" in t}

        # Fill in any missing IDs with original text (for non-punctuation segments)
        for s in translatable_segments:
            if s["id"] not in mapping:
                mapping[s["id"]] = s["text"]

        # Add punctuation segments back as-is
        mapping.update(punctuation_segments)
        self.logger.info(f"Final mapping of segment translations: {str(mapping)[:300]}{'...' if len(str(mapping)) > 300 else ''}")

        return mapping, usage, detected
