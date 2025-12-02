# data/data_store.py
# data/data_store.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

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
        st.session_state[MATCHES_KEY] = _empty_matches()

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
    """Realistische seed-organisaties voor de PoC."""
    data = [
        {
            "organisatie_id": 1,
            "organisatie_naam": "ROC Midden Nederland",
            "abonnement_type": "premium",
            "sector": "onderwijs",
            "type_organisatie": "MBO-instelling",
            "omzet": 320_000_000,
            "aantal_medewerkers": 3000,
            "locatie": "Utrecht",
            "organisatieprofiel": (
                "Grote regionale MBO-instelling met meerdere locaties en een sterke focus op "
                "digitale didactiek, hybride onderwijs, praktijkleren en innovatieprogramma's "
                "rond techniek, zorg en ICT. Organisatie werkt actief samen met bedrijven en "
                "kennisinstellingen om digitale leerlijnen en adaptieve leermiddelen te ontwikkelen."
            ),
            "website_link": "https://www.rocmn.nl",
        },
        {
            "organisatie_id": 2,
            "organisatie_naam": "Blue Analytics BV",
            "abonnement_type": "basic",
            "sector": "zakelijke dienstverlening",
            "type_organisatie": "Data- en AI-consultancy",
            "omzet": 4_200_000,
            "aantal_medewerkers": 28,
            "locatie": "Amsterdam",
            "organisatieprofiel": (
                "Specialistisch consultancybureau dat organisaties ondersteunt bij het ontwikkelen "
                "van data-gedreven strategieën. Expertise in machine learning, voorspellende modellen, "
                "procesautomatisering en AI-implementaties voor mkb en grootzakelijke klanten. "
                "Organisatie werkt aan innovatieprojecten met universiteiten en overheidsprogramma’s "
                "voor digitale transformatie."
            ),
            "website_link": "https://www.blueanalytics.nl",
        },
        {
            "organisatie_id": 3,
            "organisatie_naam": "Zorggroep West-Brabant",
            "abonnement_type": "premium",
            "sector": "zorg",
            "type_organisatie": "VVT-instelling",
            "omzet": 185_000_000,
            "aantal_medewerkers": 2600,
            "locatie": "Breda",
            "organisatieprofiel": (
                "Regionale VVT-zorgaanbieder met diverse locaties voor ouderenzorg, wijkverpleging en "
                "behandeling. Sterke focus op digitale zorgoplossingen zoals monitoring op afstand, "
                "beeldzorg, domotica en inzet van hybride zorgmodellen. Organisatie participeert in "
                "meerdere innovatieprogramma’s voor technologie in de langdurige zorg."
            ),
            "website_link": "https://www.zgwb.nl",
        },
    ]

    return pd.DataFrame(data)


def _seed_subsidies() -> pd.DataFrame:
    """Dummy-subsidies voor de PoC, gebaseerd op bestaande regelingen."""
    today = datetime.today().date()

    data = [
        # 1. MIT: R&D-samenwerkingsprojecten AI (RVO)
        {
            "subsidie_id": 1,
            "subsidie_naam": "MIT R&D-samenwerkingsprojecten AI",
            "bron": "RVO",
            "datum_toegevoegd": today - timedelta(days=30),
            "sluitingsdatum": today + timedelta(days=60),
            "subsidiebedrag": (
                "Subsidie voor R&D-samenwerkingsprojecten met AI als thema. "
                "Indicatief: circa 35% van projectkosten met maximale bedragen "
                "voor kleine en grote samenwerkingsprojecten (afhankelijk van de call)."
            ),
            "voor_wie": (
                "Mkb-ondernemingen die in een samenwerkingsverband werken aan R&D-projecten "
                "voor de ontwikkeling of vernieuwing van producten, diensten of processen, "
                "met duidelijke inzet van artificiële intelligentie."
            ),
            "samenvatting_eisen": (
                "- Project is een samenwerkingsproject tussen minimaal twee mkb-ondernemingen\n"
                "- Draagt aantoonbaar bij aan ontwikkeling en inzet van AI in producten of processen\n"
                "- Realistische planning en begroting, met technische haalbaarheid\n"
                "- Voldoende eigen inbreng en financiering door de deelnemers\n"
            ),
            "subsidie_tekst_volledig": (
                "Met de MIT R&D-samenwerkingsprojecten AI kunnen mkb-ondernemingen samen "
                "investeren in de ontwikkeling van nieuwe AI-oplossingen. De regeling is gericht "
                "op projecten waarin meerdere bedrijven samenwerken aan vernieuwende producten, "
                "diensten of productieprocessen waarbij artificiële intelligentie een centrale rol "
                "speelt. Het project moet bijdragen aan de verdere ontwikkeling en toepassing van "
                "AI in de praktijk, bijvoorbeeld door nieuwe algoritmen, toepassingen of tooling te "
                "ontwikkelen. In de beoordeling wordt gelet op de innovatiehoogte, de economische "
                "impact, de kwaliteit van de samenwerking en de haalbaarheid van de plannen. "
                "De subsidie vergoedt een deel van de subsidiabele projectkosten, tot een maximum "
                "dat verschilt per call en projectomvang. De regeling is onderdeel van de MIT "
                "instrumenten en wordt via RVO verstrekt."
            ),
            "weblink": "https://www.rvo.nl/subsidies-financiering/mit/rd-samenwerkingsprojecten-ai",
        },

        # 2. Praktijkgericht onderzoek naar opschaling van digitale/hybride zorg (ZonMw)
        {
            "subsidie_id": 2,
            "subsidie_naam": "Praktijkonderzoek naar opschaling van digitale en hybride zorg",
            "bron": "ZonMw",
            "datum_toegevoegd": today - timedelta(days=20),
            "sluitingsdatum": today + timedelta(days=90),
            "subsidiebedrag": (
                "Totaalbudget enkele miljoenen euro; per project indicatief tussen "
                "€50.000 en €300.000, afhankelijk van type onderzoek en omvang van de opschaling."
            ),
            "voor_wie": (
                "Zorg- en welzijnsorganisaties, kennisinstellingen en consortia die praktijkgericht "
                "onderzoek willen doen naar de opschaling van digitale en hybride zorgprocessen."
            ),
            "samenvatting_eisen": (
                "- Focus op opschaling van bestaande digitale of hybride zorgtoepassingen\n"
                "- Praktijkgericht onderzoek samen met zorgprofessionals en cliënten\n"
                "- Aandacht voor randvoorwaarden zoals organisatie, financiën en implementatie\n"
                "- Resultaten moeten herbruikbaar en overdraagbaar zijn naar andere organisaties\n"
            ),
            "subsidie_tekst_volledig": (
                "Deze ZonMw-ronde richt zich op praktijkgericht onderzoek naar de opschaling van "
                "digitale en hybride zorg. Het gaat niet om het ontwikkelen van volledig nieuwe "
                "technologie, maar om het onderbouwen en verbeteren van het grootschalig gebruik van "
                "bestaande digitale toepassingen in de zorgpraktijk. Projecten brengen in kaart wat "
                "nodig is om digitale zorg duurzaam te implementeren in werkprocessen, hoe professionals "
                "en cliënten worden meegenomen, welke organisatorische veranderingen vereist zijn en "
                "hoe financiering en bekostiging kunnen worden ingericht. De consortia bestaan bij "
                "voorkeur uit zorgaanbieders, kennisinstellingen en eventueel leveranciers of andere "
                "partners. De subsidie dekt een substantieel deel van de projectkosten; mede-financiering "
                "en inzet van betrokken organisaties worden verwacht. Resultaten moeten bruikbaar zijn voor "
                "andere instellingen, bijvoorbeeld via publicaties, handreikingen en implementatieplannen."
            ),
            "weblink": "https://www.zonmw.nl/nl/subsidie/praktijkgericht-onderzoek-naar-opschaling-van-digitale-hybride-zorg",
        },

        # 3. Implementatie- en opschalingscoaching Ouderen Thuis (Zorg voor innoveren / ZonMw)
        {
            "subsidie_id": 3,
            "subsidie_naam": "Implementatie- en opschalingscoaching Ouderen Thuis",
            "bron": "ZonMw",
            "datum_toegevoegd": today - timedelta(days=10),
            "sluitingsdatum": today + timedelta(days=45),
            "subsidiebedrag": (
                "Relatief kleinschalige subsidie per project voor het inzetten van een "
                "implementatie- en opschalingscoach, gericht op het verder brengen van "
                "bestaande zorginnovaties voor ouderen thuis."
            ),
            "voor_wie": (
                "Zorgorganisaties en consortia die al een innovatie voor ouderen thuis in gebruik hebben "
                "en ondersteuning zoeken om deze beter, sneller en duurzamer te implementeren of op te schalen."
            ),
            "samenvatting_eisen": (
                "- Innovatie is al ontwikkeld en in de praktijk getest of in gebruik\n"
                "- Doel is opschaling of duurzame inbedding bij ouderen thuis\n"
                "- Inzet van een implementatie- en opschalingscoach is duidelijk beschreven\n"
                "- Heldere doelstellingen, beoogde resultaten en borgingsplan\n"
            ),
            "subsidie_tekst_volledig": (
                "Met de regeling Implementatie- en opschalingscoaching Ouderen Thuis ondersteunt ZonMw "
                "zorginnovatoren die hun bestaande innovatie voor ouderen thuis breder willen invoeren. "
                "De subsidie is bedoeld om een onafhankelijke coach in te schakelen die helpt bij het uitwerken "
                "van een implementatiestrategie, het wegnemen van knelpunten en het organiseren van opschaling. "
                "Voorbeelden zijn digitale toepassingen voor monitoring, communicatie of ondersteuning van "
                "mantelzorgers. Projecten richten zich op het beter, sneller en duurzamer implementeren van "
                "de innovatie in de dagelijkse zorgpraktijk. De coach helpt bij het betrekken van alle relevante "
                "stakeholders, het inrichten van processen, het borgen van kwaliteit en het verkennen van structurele "
                "financiering. De regeling komt voort uit het programma Zorg voor innoveren en sluit aan bij de "
                "ambitie om ouderen zo lang mogelijk zelfstandig en ondersteund thuis te laten wonen."
            ),
            "weblink": "https://www.zonmw.nl/nl/subsidie/implementatie-en-opschalingscoaching-ouderen-thuis-ronde-3",
        },
    ]

    df = pd.DataFrame(data)
    df["datum_toegevoegd"] = pd.to_datetime(df["datum_toegevoegd"])
    df["sluitingsdatum"] = pd.to_datetime(df["sluitingsdatum"])
    return df


def _empty_matches() -> pd.DataFrame:
    """Lege matches-tabel, tot de gebruiker op 'Genereer matches' drukt."""
    columns = [
        "match_id",
        "subsidie_id",
        "organisatie_id",
        "persona_id",         # blijft bestaan voor schema-compatibiliteit
        "type",               # 'organisatie' of 'persona'
        "match_score",
        "match_toelichting",
        "datum_toegevoegd",
    ]
    return pd.DataFrame(columns=columns)

def _seed_newsletters() -> pd.DataFrame:
    """Lege dummy-nieuwsbrieven-tabel."""
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
            "naam": "Standaard organisatiematch (volledige data)",
            "prompt_template": (
                "Je bent een formele subsidie-analist. "
                "Bepaal op een schaal van 1 tot 100 hoe goed deze ORGANISATIE past "
                "bij de onderstaande SUBSIDIE. Baseer je uitsluitend op de aangeleverde data.\n\n"

                "==============================\n"
                "ORGANISATIE-INFORMATIE\n"
                "==============================\n"
                "ID: {organisatie_id}\n"
                "Naam: {organisatie_naam}\n"
                "Sector: {sector}\n"
                "Type organisatie: {type_organisatie}\n"
                "Locatie: {locatie}\n"
                "Omzet: {omzet}\n"
                "Aantal medewerkers: {aantal_medewerkers}\n"
                "Abonnementstype: {abonnement_type}\n"
                "Website: {website_link}\n\n"
                "Profiel:\n"
                "{organisatieprofiel}\n\n"

                "==============================\n"
                "SUBSIDIE-INFORMATIE\n"
                "==============================\n"
                "ID: {subsidie_id}\n"
                "Naam: {subsidie_naam}\n"
                "Bron: {bron}\n"
                "Datum toegevoegd: {datum_toegevoegd}\n"
                "Sluitingsdatum: {sluitingsdatum}\n"
                "Subsidiebedrag: {subsidiebedrag}\n\n"

                "Voor wie:\n"
                "{voor_wie}\n\n"

                "Samenvatting eisen:\n"
                "{samenvatting_eisen}\n\n"

                "Volledige subsidie-tekst:\n"
                "{subsidie_tekst_volledig}\n\n"
                "Link: {weblink}\n\n"

                "==============================\n"
                "INSTRUCTIE\n"
                "==============================\n"
                "Analyseer de fit op basis van inhoudelijke aansluiting, doelgroep, "
                "voorwaarden, schaal, technische domeinen, sector en organisatorische kenmerken.\n"
                "Overweeg expliciet of de organisatie past binnen de vereisten, "
                "de thematiek en de doelstelling van de subsidie.\n\n"

                "Produceer alleen de volgende JSON-output:\n"
                "{\n"
                '  "match_score": <integer tussen 1 en 100>,\n'
                '  "match_toelichting": [\n'
                '    "korte bullet over de aansluiting",\n'
                '    "korte bullet over sterke punten of tekortkomingen",\n'
                '    "korte bullet ter motivatie van de score"\n'
                "  ]\n"
                "}\n"
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


def get_active_prompt() -> Optional[Dict[str, Any]]:
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
