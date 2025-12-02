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
    org: Dict[str, Any],
    subsidie: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Bepaal match-score en toelichting voor een organisatie + subsidie.

    Maakt ALLE relevante velden van organisatie en subsidie beschikbaar
    als placeholders in het prompt-template.
    """

    def _fmt_date(value: Any) -> str:
        if value is None:
            return ""
        try:
            return str(pd.to_datetime(value).date())
        except Exception:
            return str(value)

    ctx = {
        # Organisatievelden
        "organisatie_id": org.get("organisatie_id", ""),
        "organisatie_naam": org.get("organisatie_naam", ""),
        "abonnement_type": org.get("abonnement_type", ""),
        "sector": org.get("sector", ""),
        "type_organisatie": org.get("type_organisatie", ""),
        "omzet": org.get("omzet", ""),
        "aantal_medewerkers": org.get("aantal_medewerkers", ""),
        "locatie": org.get("locatie", ""),
        "organisatieprofiel": org.get("organisatieprofiel", ""),
        "website_link": org.get("website_link", ""),

        # Subsidievelden
        "subsidie_id": subsidie.get("subsidie_id", ""),
        "subsidie_naam": subsidie.get("subsidie_naam", ""),
        "bron": subsidie.get("bron", ""),
        "datum_toegevoegd": _fmt_date(subsidie.get("datum_toegevoegd")),
        "sluitingsdatum": _fmt_date(subsidie.get("sluitingsdatum")),
        "subsidiebedrag": subsidie.get("subsidiebedrag", ""),
        "voor_wie": subsidie.get("voor_wie", ""),
        "samenvatting_eisen": subsidie.get("samenvatting_eisen", ""),
        "subsidie_tekst_volledig": subsidie.get("subsidie_tekst_volledig", ""),
        "weblink": subsidie.get("weblink", ""),
    }

    prompt = prompt_template.format(**ctx)

    if self._client is None:
        return self._mock_response(org, subsidie)

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
    @staticmethod
def _mock_response(
    org: Dict[str, Any], subsidie: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mock-respons op basis van simpele heuristiek, zodat de PoC werkt zonder API-key.
    """
    base = 60
    profile = str(org.get("organisatieprofiel", "")).lower()
    naam = str(subsidie.get("subsidie_naam", "")).lower()

    if "onderwijs" in profile or "school" in profile or "mbo" in profile:
        if "onderwijs" in naam or "digitale" in naam:
            base = 85
    if "zorg" in profile or "thuiszorg" in profile or "ouderenzorg" in profile:
        if "zorg" in naam or "thuis" in naam:
            base = 82
    if "ai" in profile or "data" in profile:
        if "ai" in naam or "data" in naam:
            base = 90

    score = max(40, min(95, base))

    bullets = [
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
