# services/llm_client.py
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import streamlit as st

try:
    # Nieuwe OpenAI client (v1+)
    from openai import OpenAI

    _HAS_OPENAI = True
except ImportError:  # pragma: no cover
    OpenAI = None  # type: ignore
    _HAS_OPENAI = False


class LLMClient:
    """
    Wrapper rond een LLM-provider voor het bepalen van match-scores.

    Voor de PoC:
    - als OPENAI_API_KEY aanwezig is in st.secrets -> echte API-call
    - anders -> deterministische mock-respons, zodat de app altijd werkt
    """

    def __init__(self) -> None:
        self._api_key: Optional[str] = st.secrets.get("OPENAI_API_KEY", None)
        self._client = None
        if self._api_key and _HAS_OPENAI:
            self._client = OpenAI(api_key=self._api_key)

    def is_real(self) -> bool:
        """True als er een echte LLM-backend beschikbaar is."""
        return self._client is not None

    def score_match_org_subsidy(
        self,
        prompt_template: str,
        organisatieprofiel: str,
        subsidie: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Bepaal match-score en toelichting voor een organisatie + subsidie.

        Verwacht een prompt-template met placeholders:
        - {organisatieprofiel}
        - {subsidie_naam}
        - {bron}
        - {voor_wie}
        - {samenvatting_eisen}

        Retourneert dict:
        {
            "match_score": int,
            "match_toelichting": List[str]
        }
        """
        prompt = prompt_template.format(
            organisatieprofiel=organisatieprofiel,
            subsidie_naam=subsidie.get("subsidie_naam", ""),
            bron=subsidie.get("bron", ""),
            voor_wie=subsidie.get("voor_wie", ""),
            samenvatting_eisen=subsidie.get("samenvatting_eisen", ""),
        )

        if self._client is None:
            return self._mock_response(organisatieprofiel, subsidie)

        return self._call_openai(prompt)

    # ------------------------------------------------------------
    # Interne helpers
    # ------------------------------------------------------------

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """
        Doe een API-call naar OpenAI en parse de JSON-uitkomst.

        Verwacht dat het model een JSON-object retourneert met keys:
        - match_score
        - match_toelichting (lijst van bullets)
        """
        try:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Je bent een hulpmiddel voor subsidiebeoordeling. "
                            "Je antwoordt strikt in JSON volgens de gevraagde structuur."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            content = response.choices[0].message.content  # type: ignore[index]
            if not content:
                return self._fallback_default()

            # Probeer JSON direct te parsen
            parsed = self._safe_json_parse(content)
            if parsed is None:
                return self._fallback_default()

            score = int(parsed.get("match_score", 50))
            toelichting = parsed.get("match_toelichting", [])

            if not isinstance(toelichting, list):
                toelichting = [str(toelichting)]

            return {
                "match_score": max(1, min(100, score)),
                "match_toelichting": [str(b) for b in toelichting],
            }

        except Exception:
            return self._fallback_default()

    @staticmethod
    def _safe_json_parse(content: str) -> Optional[Dict[str, Any]]:
        """
        Probeer verschillende eenvoudige strategieën om JSON uit een string te halen.
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Tweede poging: content tussen eerste { en laatste }
        if "{" in content and "}" in content:
            start = content.find("{")
            end = content.rfind("}") + 1
            snippet = content[start:end]
            try:
                return json.loads(snippet)
            except json.JSONDecodeError:
                return None
        return None

    @staticmethod
    def _fallback_default() -> Dict[str, Any]:
        """Fallback als parsing of API-call faalt."""
        return {
            "match_score": 50,
            "match_toelichting": [
                "Standaard score gebruikt omdat de LLM-respons niet verwerkbaar was."
            ],
        }

    @staticmethod
    def _mock_response(
        organisatieprofiel: str, subsidie: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mock-respons op basis van simpele heuristiek, zodat de PoC werkt zonder API-key.
        """
        base = 60
        profile = organisatieprofiel.lower()
        naam = str(subsidie.get("subsidie_naam", "")).lower()

        if "onderwijs" in profile or "school" in profile:
            if "onderwijs" in naam or "digitale" in naam:
                base = 85
        if "zorg" in profile or "thuiszorg" in profile:
            if "zorg" in naam or "thuis" in naam:
                base = 82
        if "ai" in profile or "data" in profile:
            if "ai" in naam or "data" in naam:
                base = 90

        score = max(40, min(95, base))

        bullets: List[str] = [
            f"Mock-score gebaseerd op overlap tussen organisatieprofiel en subsidie '{subsidie.get('subsidie_naam', '')}'.",
            "Deze score is gegenereerd zonder echte LLM-call (demo-modus).",
        ]

        return {
            "match_score": score,
            "match_toelichting": bullets,
        }


# Singleton-achtige accessor, zodat niet overal een nieuwe client wordt aangemaakt
_CLIENT_INSTANCE: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Geef een gedeelde LLMClient-instantie terug."""
    global _CLIENT_INSTANCE
    if _CLIENT_INSTANCE is None:
        _CLIENT_INSTANCE = LLMClient()
    return _CLIENT_INSTANCE
