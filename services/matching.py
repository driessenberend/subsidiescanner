# services/matching.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd
import streamlit as st

from data.data_store import (
    ACTIVE_PROMPT_ID_KEY,
    MATCHES_KEY,
    ORGANISATIONS_KEY,
    PERSONAS_KEY,
    SUBSIDIES_KEY,
    get_active_prompt,
    get_table,
    next_id,
    set_table,
)
from services.llm_client import get_llm_client


def recompute_all_matches() -> None:
    """
    Herbereken alle matches voor:
    - alle organisaties x alle subsidies
    - alle persona's x alle subsidies

    Vervangt de huidige matches-tabel volledig.
    """
    organisations_df = get_table(ORGANISATIONS_KEY)
    subsidies_df = get_table(SUBSIDIES_KEY)
    personas_df = get_table(PERSONAS_KEY)

    prompt_record = get_active_prompt()
    if prompt_record is None:
        st.warning("Er is geen actieve prompt geconfigureerd. Kan matches niet herberekenen.")
        return

    prompt_template = prompt_record["prompt_template"]
    llm_client = get_llm_client()

    all_rows = []

    # Organisatie-matches
    for _, org in organisations_df.iterrows():
        for _, sub in subsidies_df.iterrows():
            row = _compute_single_match_org(
                org.to_dict(), sub.to_dict(), prompt_template, llm_client
            )
            all_rows.append(row)

    # Persona-matches
    for _, persona in personas_df.iterrows():
        for _, sub in subsidies_df.iterrows():
            row = _compute_single_match_persona(
                persona.to_dict(), sub.to_dict(), prompt_template, llm_client
            )
            all_rows.append(row)

    if all_rows:
        matches_df = pd.DataFrame(all_rows)
        matches_df["datum_toegevoegd"] = pd.to_datetime(matches_df["datum_toegevoegd"])
    else:
        matches_df = pd.DataFrame(
            columns=[
                "match_id",
                "subsidie_id",
                "organisatie_id",
                "persona_id",
                "type",
                "match_score",
                "match_toelichting",
                "datum_toegevoegd",
            ]
        )

    set_table(MATCHES_KEY, matches_df)


def _compute_single_match_org(
    org: Dict[str, Any],
    subsidie: Dict[str, Any],
    prompt_template: str,
    llm_client,
) -> Dict[str, Any]:
    """
    Bereken match voor één organisatie + één subsidie.
    """
    result = llm_client.score_match_org_subsidy(
        prompt_template=prompt_template,
        organisatieprofiel=org.get("organisatieprofiel", ""),
        subsidie=subsidie,
    )

    match_id = _temp_match_id()
    today = datetime.today()

    return {
        "match_id": match_id,
        "subsidie_id": subsidie["subsidie_id"],
        "organisatie_id": org["organisatie_id"],
        "persona_id": None,
        "type": "organisatie",
        "match_score": int(result.get("match_score", 50)),
        "match_toelichting": "\n".join(result.get("match_toelichting", [])),
        "datum_toegevoegd": today,
    }


def _compute_single_match_persona(
    persona: Dict[str, Any],
    subsidie: Dict[str, Any],
    prompt_template: str,
    llm_client,
) -> Dict[str, Any]:
    """
    Bereken match voor één persona + één subsidie.

    Hergebruikt hetzelfde prompt-template, met persona_omschrijving als 'organisatieprofiel'.
    """
    pseudo_profile = (
        f"Persona-sector: {persona.get('persona_sector', '')}\n"
        f"Persona-organisatietype: {persona.get('persona_organisatie_type', '')}\n\n"
        f"Omschrijving:\n{persona.get('persona_omschrijving', '')}"
    )

    result = llm_client.score_match_org_subsidy(
        prompt_template=prompt_template,
        organisatieprofiel=pseudo_profile,
        subsidie=subsidie,
    )

    match_id = _temp_match_id()
    today = datetime.today()

    return {
        "match_id": match_id,
        "subsidie_id": subsidie["subsidie_id"],
        "organisatie_id": None,
        "persona_id": persona["persona_id"],
        "type": "persona",
        "match_score": int(result.get("match_score", 50)),
        "match_toelichting": "\n".join(result.get("match_toelichting", [])),
        "datum_toegevoegd": today,
    }


# Voor een volledige reset van matches maken we tijdelijke ID's;
# bij CRUD-operaties in de UI kun je next_id(MATCHES_KEY, "match_id") gebruiken.
_TEMP_MATCH_COUNTER_KEY = "_temp_match_counter"


def _temp_match_id() -> int:
    """
    Eenvoudige teller voor match_id binnen één recompute-run.
    """
    if _TEMP_MATCH_COUNTER_KEY not in st.session_state:
        st.session_state[_TEMP_MATCH_COUNTER_KEY] = 1
    val = st.session_state[_TEMP_MATCH_COUNTER_KEY]
    st.session_state[_TEMP_MATCH_COUNTER_KEY] = val + 1
    return int(val)


def update_prompt_template(new_template: str) -> None:
    """
    Werk het actieve prompttemplate bij in de prompts-tabel.

    Data_store houdt de actieve prompt-id bij; hier wordt alleen de tekst aangepast.
    """
    prompts_df = get_table("prompts_df")
    active_prompt_id: Optional[int] = st.session_state.get(ACTIVE_PROMPT_ID_KEY)
    if active_prompt_id is None:
        return

    idx = prompts_df.index[prompts_df["prompt_id"] == active_prompt_id]
    if len(idx) == 0:
        return

    i = idx[0]
    prompts_df.at[i, "prompt_template"] = new_template
    prompts_df.at[i, "laatst_gewijzigd"] = datetime.now()

    set_table("prompts_df", prompts_df)
