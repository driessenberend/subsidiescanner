import os
import json
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

    # --------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------
    def score_match_org_subsidy(self, prompt_template, org, subsidie):
        """
        Bouw de prompt → LLM-call → interpreteer JSON.
        """

        # Context voor .format()
        ctx = {
            # organisatie
            "organisatie_id": org.get("organisatie_id", ""),
            "organisatie_naam": org.get("organisatie_naam", ""),
            "sector": org.get("sector", ""),
            "type_organisatie": org.get("type_organisatie", ""),
            "locatie": org.get("locatie", ""),
            "omzet": org.get("omzet", ""),
            "aantal_medewerkers": org.get("aantal_medewerkers", ""),
            "abonnement_type": org.get("abonnement_type", ""),
            "website_link": org.get("website_link", ""),
            "organisatieprofiel": org.get("organisatieprofiel", ""),

            # subsidie
            "subsidie_id": subsidie.get("subsidie_id", ""),
            "subsidie_naam": subsidie.get("subsidie_naam", ""),
            "bron": subsidie.get("bron", ""),
            "datum_toegevoegd": subsidie.get("datum_toegevoegd", ""),
            "sluitingsdatum": subsidie.get("sluitingsdatum", ""),
            "subsidiebedrag": subsidie.get("subsidiebedrag", ""),
            "voor_wie": subsidie.get("voor_wie", ""),
            "samenvatting_eisen": subsidie.get("samenvatting_eisen", ""),
            "subsidie_tekst_volledig": subsidie.get("subsidie_tekst_volledig", ""),
            "weblink": subsidie.get("weblink", ""),
        }

        # Formatteer de prompt veilig
        prompt = prompt_template.format_map(_SafeDict(ctx))

        # Kies mock-LLM of echte OpenAI
        if not self.is_real():
            return self._mock_response(org, subsidie)

        return self._call_openai(prompt)

    # --------------------------------------------------------
    # PRIVATE: ECHTE OPENAI CALL
    # --------------------------------------------------------
    def _call_openai(self, prompt: str):
        """
        OpenAI chat-completion call volgens nieuwe API.
        Verwacht JSON-object in response.
        """
        try:
            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Je bent een formele subsidie-analist. "
                            "Je antwoordt uitsluitend in JSON volgens de gevraagde structuur."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=400,
            )

            # Nieuwe API → message is object, geen dict → gebruik .content
            raw_json = response.choices[0].message.content
            parsed = json.loads(raw_json)

            score = int(parsed.get("match_score", 50))
            toel = parsed.get("match_toelichting", [])

            if isinstance(toel, str):
                toel = [toel]
            elif not isinstance(toel, list):
                toel = [str(toel)]

            return {
                "match_score": score,
                "match_toelichting": toel,
            }

        except Exception as exc:
            return {
                "match_score": 50,
                "match_toelichting": [
                    "Fout bij OpenAI-call.",
                    str(exc),
                ],
            }

    # --------------------------------------------------------
    # PRIVATE: MOCK (fallback)
    # --------------------------------------------------------
    def _mock_response(self, org, subsidie):
        # Zeer eenvoudige demo-respons voor non-OpenAI modus
        base_score = 40
        if subsidie.get("sector") == org.get("sector"):
            base_score += 30

        return {
            "match_score": base_score,
            "match_toelichting": [
                "Mock-modus actief (geen echte OpenAI).",
                f"Organisatie: {org.get('organisatie_naam')}",
                f"Subsidie: {subsidie.get('subsidie_naam')}",
            ],
        }


# --------------------------------------------------------
# HULP: SAFE FORMAT-DICT
# --------------------------------------------------------
class _SafeDict(dict):
    """
    Voorkomt KeyErrors in str.format_map().
    Mist een key → return "".
    """

    def __missing__(self, key):
        return ""


# --------------------------------------------------------
# FABRIEK
# --------------------------------------------------------
def get_llm_client():
    """
    Singleton LLM-client per sessie.
    """
    if "llm_client" not in st.session_state:
        st.session_state["llm_client"] = LLMClient()
    return st.session_state["llm_client"]
