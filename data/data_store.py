# data/data_store.py
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st


ORGANISATIONS_KEY = "organisations_df"
SUBSIDIES_KEY = "subsidies_df"
PERSONAS_KEY = "personas_df"
MATCHES_KEY = "matches_df"
NEWSLETTERS_KEY = "newsletters_df"
PROMPTS_KEY = "prompts_df"
ACTIVE_PROMPT_ID_KEY = "active_prompt_id"


def init_session_state() -> None:
    """Initialiseer alle in-memory tabellen in st.session_state als ze nog niet bestaan."""
    if ORGANISATIONS_KEY not in st.session_state:
        st.session_state[ORGANISATIONS_KEY] = _seed_organisations()

    if SUBSIDIES_KEY not in st.session_state:
        st.session_state[SUBSIDIES_KEY] = _seed_subsidies()

    if PERSONAS_KEY not in st.session_state:
        st.session_state[PERSONAS_KEY] = _seed_personas()

    if MATCHES_KEY not in st.session_state:
        st.session_state[MATCHES_KEY] = _seed_matches()

    if NEWSLETTERS_KEY not in st.session_state:
        st.session_state[NEWSLETTERS_KEY] = _seed_newsletters()

    if PROMPTS_KEY not in st.session_state:
        st.session_state[PROMPTS_KEY] = _seed_prompts()

    if ACTIVE_PROMPT_ID_KEY not in st.session_state:
        prompts_df = st.session_state[PROMPTS_KEY]
        if not prompts_df.empty:
            st.session_state[ACTIVE_PROMPT_ID_KEY] = int(prompts_df.iloc[0]["prompt_id"])
        else:
            st.session_state[ACTIVE_PROMPT_ID_KEY] = None


# ------------------------------------------------------------
# Seed-data
# ------------------------------------------------------------


def _seed_organisations() -> pd.DataFrame:
    """Dummy-organisaties voor de PoC."""
    data = [
        {
            "organisatie_id": 1,
            "organisatie_naam": "EduTech College",
            "abonnement_type": "premium",
            "sector": "onderwijs",
            "type_organisatie": "middelbare school",
            "omzet": 8_000_000,
            "aantal_medewerkers": 120,
            "locatie": "Utrecht",
            "organisatieprofiel": (
                "Middelgrote middelbare school met focus op digitale didactiek en "
                "samenwerkingen met techbedrijven."
            ),
            "website_link": "https://www.edutech-college.nl",
        },
        {
            "organisatie_id": 2,
            "organisatie_naam": "Bright Consultancy",
            "abonnement_type": "basic",
            "sector": "zakelijke dienstverlening",
            "type_organisatie": "IT consultant",
            "omzet": 3_500_000,
            "aantal_medewerkers": 35,
            "locatie": "Amsterdam",
            "organisatieprofiel": (
                "Consultancybureau gespecialiseerd in data-analytics en AI-oplossingen "
                "voor MKB-organisaties."
            ),
            "website_link": "https://www.bright-consultancy.nl",
        },
        {
            "organisatie_id": 3,
            "organisatie_naam": "GreenCare Zorggroep",
            "abonnement_type": "premium",
            "sector": "zorg",
            "type_organisatie": "zorginstelling",
            "omzet": 25_000_000,
            "aantal_medewerkers": 500,
            "locatie": "Rotterdam",
            "organisatieprofiel": (
                "Regionale zorginstelling met focus op ouderenzorg en innovatie in "
                "thuiszorg-technologie."
            ),
            "website_link": "https://www.greencare-zorg.nl",
        },
    ]
    return pd.DataFrame(data)


def _seed_subsidies() -> pd.DataFrame:
    """Dummy-subsidies voor de PoC."""
    today = datetime.today().date()
    data = [
        {
            "subsidie_id": 1,
            "subsidie_naam": "Digitale Innovatie Onderwijs 2025",
            "bron": "ZonMw",
            "datum_toegevoegd": today - timedelta(days=10),
            "sluitingsdatum": today + timedelta(days=40),
            "subsidiebedrag": "Maximaal 700.000 EUR, 50% eigen inleg",
            "voor_wie": (
                "Onderwijsinstellingen die digitale innovaties willen implementeren in het curriculum."
            ),
            "samenvatting_eisen": (
                "- Project met aantoonbare impact op leeruitkomsten\n"
                "- Minimaal 2 samenwerkingspartners\n"
                "- Co-financiering van 50%\n"
            ),
            "weblink": "https://www.example.org/subsidies/digitale-innovatie-onderwijs-2025",
        },
        {
            "subsidie_id": 2,
            "subsidie_naam": "AI en Data in het MKB",
            "bron": "RVO",
            "datum_toegevoegd": today - timedelta(days=25),
            "sluitingsdatum": today + timedelta(days=15),
            "subsidiebedrag": "Tussen 50.000 en 250.000 EUR, 30% eigen inleg",
            "voor_wie": (
                "MKB-bedrijven die AI- en data-oplossingen willen ontwikkelen of implementeren."
            ),
            "samenvatting_eisen": (
                "- Focus op innovatie in processen of diensten\n"
                "- Realistische businesscase\n"
                "- Samenwerking met kennisinstelling aanbevolen\n"
            ),
            "weblink": "https://www.example.org/subsidies/ai-data-mkb",
        },
        {
            "subsidie_id": 3,
            "subsidie_naam": "Zorginnovatie Thuis 2025",
            "bron": "ZonMw",
            "datum_toegevoegd": today - timedelta(days=5),
            "sluitingsdatum": today + timedelta(days=60),
            "subsidiebedrag": "Maximaal 500.000 EUR, 40% eigen inleg",
            "voor_wie": (
                "Zorginstellingen en consortia gericht op digitale innovatie in de thuiszorg."
            ),
            "samenvatting_eisen": (
                "- Aantoonbare verbetering kwaliteit van zorg\n"
                "- Participatie van cliënten\n"
                "- Opschaalbaarheid na pilotfase\n"
            ),
            "weblink": "https://www.example.org/subsidies/zorginnovatie-thuis-2025",
        },
    ]
    df = pd.DataFrame(data)
    # Zorg dat datumkolommen als datetime worden opgeslagen
    df["datum_toegevoegd"] = pd.to_datetime(df["datum_toegevoegd"])
    df["sluitingsdatum"] = pd.to_datetime(df["sluitingsdatum"])
    return df


def _seed_personas() -> pd.DataFrame:
    """Dummy-persona's voor de PoC."""
    data = [
        {
            "persona_id": 1,
            "persona_sector": "onderwijs",
            "persona_organisatie_type": "middelbare school",
            "persona_omschrijving": (
                "Innovatiecoördinator bij een middelbare school die digitale leermiddelen "
                "en blended learning wil opschalen."
            ),
        },
        {
            "persona_id": 2,
            "persona_sector": "zakelijke dienstverlening",
            "persona_organisatie_type": "IT consultant",
            "persona_omschrijving": (
                "Partner bij IT-consultancy, zoekt subsidies voor het ontwikkelen van een "
                "AI-gedreven adviesplatform."
            ),
        },
        {
            "persona_id": 3,
            "persona_sector": "zorg",
            "persona_organisatie_type": "zorginstelling",
            "persona_omschrijving": (
                "Innovatiemanager die technologie wil inzetten om personeelstekorten in de zorg "
                "op te vangen."
            ),
        },
    ]
    return pd.DataFrame(data)


def _seed_matches() -> pd.DataFrame:
    """Eerste dummy-matches, alsof er al een LLM-run is geweest."""
    today = datetime.today().date()
    data = [
        {
            "match_id": 1,
            "subsidie_id": 1,
            "organisatie_id": 1,
            "persona_id": None,
            "type": "organisatie",
            "match_score": 88,
            "match_toelichting": (
                "- Sterke fit met digitale innovatie in onderwijs\n"
                "- School heeft bestaande digitale strategie\n"
                "- Samenwerking met techpartners sluit aan op subsidievoorwaarden"
            ),
            "datum_toegevoegd": today - timedelta(days=7),
        },
        {
            "match_id": 2,
            "subsidie_id": 2,
            "organisatie_id": 2,
            "persona_id": None,
            "type": "organisatie",
            "match_score": 91,
            "match_toelichting": (
                "- Consultancy focust op AI en data, sluit direct aan\n"
                "- MKB-doelgroep is expliciet benoemd in de regeling\n"
                "- Potentie voor schaalbare oplossing"
            ),
            "datum_toegevoegd": today - timedelta(days=3),
        },
        {
            "match_id": 3,
            "subsidie_id": 3,
            "organisatie_id": 3,
            "persona_id": None,
            "type": "organisatie",
            "match_score": 85,
            "match_toelichting": (
                "- Zorginstelling met duidelijke focus op thuiszorg\n"
                "- Ambitie op digitale innovatie komt terug in profiel\n"
                "- Subsidie eist concrete verbetering kwaliteit zorg"
            ),
            "datum_toegevoegd": today - timedelta(days=2),
        },
    ]
    df = pd.DataFrame(data)
    df["datum_toegevoegd"] = pd.to_datetime(df["datum_toegevoegd"])
    return df


def _seed_newsletters() -> pd.DataFrame:
    """Optioneel wat dummy-nieuwsbrieven, maar standaard leeg gelaten."""
    columns = [
        "nieuwsbrief_id",
        "organisatie_id",
        "organisatie_naam",
        "nieuwsbrief_datum",
        "nieuwsbrief_content",
    ]
    return pd.DataFrame(columns=columns)


def _seed_prompts() -> pd.DataFrame:
    """Tabel met gebruikte prompts voor matching."""
    today = datetime.today()
    data = [
        {
            "prompt_id": 1,
            "naam": "Standaard organisatiematch",
            "prompt_template": (
                "Je bent een subsidie-analist. Bepaal op een schaal van 1 tot 100 hoe goed de "
                "volgende organisatie past bij de onderstaande subsidie.\n\n"
                "ORGANISATIEPROFIEL:\n"
                "{organisatieprofiel}\n\n"
                "SUBSIDIE-INFORMATIE:\n"
                "Naam: {subsidie_naam}\n"
                "Bron: {bron}\n"
                "Voor wie: {voor_wie}\n"
                "Samenvatting eisen:\n"
                "{samenvatting_eisen}\n\n"
                "Geef een JSON-respons met exact de volgende velden:\n"
                "{{\n"
                '  "match_score": <integer tussen 1 en 100>,\n'
                '  "match_toelichting": [\n'
                "    \"korte bullet 1\",\n"
                "    \"korte bullet 2\",\n"
                "    \"korte bullet 3\"\n"
                "  ]\n"
                "}}\n"
            ),
            "laatst_gewijzigd": today,
            "actief": True,
        }
    ]
    df = pd.DataFrame(data)
    df["laatst_gewijzigd"] = pd.to_datetime(df["laatst_gewijzigd"])
    return df


# ------------------------------------------------------------
# Hulpfuncties om tabellen te benaderen en ID's te genereren
# ------------------------------------------------------------


def get_table(key: str) -> pd.DataFrame:
    """Geef een DataFrame uit session_state. Referentie, geen kopie."""
    return st.session_state[key]


def set_table(key: str, df: pd.DataFrame) -> None:
    """Overschrijf een DataFrame in session_state."""
    st.session_state[key] = df


def next_id(table_key: str, id_column: str) -> int:
    """Genereer een nieuw integer-ID voor een gegeven tabel."""
    df = st.session_state[table_key]
    if df.empty:
        return 1
    max_val = pd.to_numeric(df[id_column], errors="coerce").max()
    if pd.isna(max_val):
        return 1
    return int(max_val) + 1


def get_active_prompt() -> dict | None:
    """Geef het actieve promptrecord als dict."""
    prompts_df = st.session_state[PROMPTS_KEY]
    active_id = st.session_state.get(ACTIVE_PROMPT_ID_KEY)
    if active_id is None or prompts_df.empty:
        return None
    record = prompts_df.loc[prompts_df["prompt_id"] == active_id]
    if record.empty:
        return None
    return record.iloc[0].to_dict()


def set_active_prompt_id(prompt_id: int) -> None:
    """Stel een prompt in als actief."""
    st.session_state[ACTIVE_PROMPT_ID_KEY] = int(prompt_id)
