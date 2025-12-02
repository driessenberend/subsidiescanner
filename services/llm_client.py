# services/llm_client.py

from __future__ import annotations

import os
from typing import Any, Dict, List

import pandas as pd
import streamlit as st


class LLMClient:
    """
    Wrapper rond OpenAI of een mock-LLM afhankelijk van de omgeving.
    """

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", None)
        self._api_key = api_key

        if api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=api_key)
            except Exception:
                self._client = None
        else:
            self._client = None

    def is_real(self) -> bool:
        return self._client is not None

    #
    # -------------------------------
    #  ORGANISATIE × SUBSIDIE MATCHER
    # -------------------------------
    #

    def score_match_org_subsidy(
        self,
        prompt_template: str,
        org: Dict[str, Any],
        subsidie: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Bepaal match-score en toelichting voor een organisatie + subsidie.
        """

        def _fmt_date(value: Any) -> str:
            if value is None:
                return ""
            try:
                return str(pd.to_datetime(value).date())
            except Exception:
                return str(value)

        # context met ALLE velden die we beschikbaar willen maken
        ctx = {
            # Organisatie
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

            # Subsidie
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

    #
    # -----------------------
    #  MOCK FALLBACK LOGICA
    # -----------------------
    #

    @staticmethod
    def _mock_response(org: Dict[str, Any], subsidie: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock-matchscore voor wanneer geen OPENAI_API_KEY beschikbaar is.
        """
        base = 60
        profile = str(org.get("organisatieprofiel", "")).lower()
        name = str(subsidie.get("subsidie_naam", "")).lower()

        if "onderwijs" in profile or "school" in profile or "mbo" in profile:
            if "onderwijs" in name or "digitale" in name:
                base = 85

        if "zorg" in profile or "oudere" in profile or "thuiszorg" in profile:
            if "zorg" in name or "thuis" in name:
                base = 82

        if "ai" in profile or "data" in profile:
            if "ai" in name or "data" in name:
                base = 90

        score = max(40, min(95, base))

        bullets = [
            f"Mock-score gebaseerd op overlap tussen organisatieprofiel en subsidie '{subsidie.get('subsidie_naam','')}'.",
            "Demo-modus: geen echte LLM-call gedaan.",
        ]

        return {
            "match_score": score,
            "match_toelichting": bullets,
        }

    #
    # ------------------------
    #  OPENAI AANROEP
    # ------------------------
    #

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """
        Echte OpenAI-inferentie.
        """
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
            )

            raw = response.choices[0].message["content"]

            import json
            parsed = json.loads(raw)

            return {
                "match_score": parsed.get("match_score", 50),
                "match_toelichting": parsed.get("match_toelichting", []),
            }
        except Exception as exc:
            return {
                "match_score": 50,
                "match_toelichting": [
                    "Fout bij OpenAI-call.",
                    f"{exc}",
                ],
            }


#
# ------------------------
#  FACTORY
# ------------------------
#

def get_llm_client() -> LLMClient:
    if "_llm_client" not in st.session_state:
        st.session_state["_llm_client"] = LLMClient()
    return st.session_state["_llm_client"]
