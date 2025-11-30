# views/personas.py
import streamlit as st
import pandas as pd

from data.data_store import (
    MATCHES_KEY,
    PERSONAS_KEY,
    SUBSIDIES_KEY,
    get_table,
    next_id,
    set_table,
)


def render_personas() -> None:
    st.title("Personas")

    personas_df = get_table(PERSONAS_KEY).copy()

    st.subheader("Filters")
    filters = _render_filters(personas_df)
    filtered = _apply_filters(personas_df, filters)

    st.subheader("Overzicht persona's")
    st.dataframe(
        filtered[
            [
                "persona_id",
                "persona_sector",
                "persona_organisatie_type",
                "persona_omschrijving",
            ]
        ],
        use_container_width=True,
    )

    st.markdown("---")
    cols = st.columns([2, 1])
    with cols[0]:
        _render_persona_detail(personas_df)
    with cols[1]:
        _render_add_delete_persona(personas_df)


def _render_filters(df: pd.DataFrame) -> dict:
    col_sector, col_type, col_search = st.columns([1, 1, 2])

    with col_sector:
        sectors = ["Alle"] + sorted(df["persona_sector"].dropna().unique().tolist())
        sector_filter = st.selectbox("Sector", sectors)

    with col_type:
        types = ["Alle"] + sorted(
            df["persona_organisatie_type"].dropna().unique().tolist()
        )
        type_filter = st.selectbox("Type organisatie", types)

    with col_search:
        search_text = st.text_input("Zoek in omschrijving", "")

    return {
        "sector_filter": sector_filter,
        "type_filter": type_filter,
        "search_text": search_text.strip().lower(),
    }


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df.copy()

    if filters["sector_filter"] != "Alle":
        out = out[out["persona_sector"] == filters["sector_filter"]]

    if filters["type_filter"] != "Alle":
        out = out[out["persona_organisatie_type"] == filters["type_filter"]]

    if filters["search_text"]:
        text = filters["search_text"]
        mask = out["persona_omschrijving"].str.lower().str.contains(text)
        out = out[mask]

    return out


def _render_persona_detail(personas_df: pd.DataFrame) -> None:
    st.subheader("Detailpersona")

    if personas_df.empty:
        st.info("Geen persona's beschikbaar.")
        return

    options = personas_df.copy()
    options["label"] = (
        options["persona_id"].astype(str)
        + " – "
        + options["persona_sector"]
        + " / "
        + options["persona_organisatie_type"]
    )

    selected_label = st.selectbox(
        "Kies persona",
        options=options["label"].tolist(),
    )
    row = options[options["label"] == selected_label].iloc[0]
    persona_id = int(row["persona_id"])

    with st.form(key=f"persona_edit_form_{persona_id}"):
        sector = st.text_input(
            "Sector",
            value=row["persona_sector"],
        )
        type_org = st.text_input(
            "Type organisatie",
            value=row["persona_organisatie_type"],
        )
        omschrijving = st.text_area(
            "Omschrijving",
            value=row["persona_omschrijving"],
            height=150,
        )

        submitted = st.form_submit_button("Opslaan wijzigingen")

    if submitted:
        _update_persona(personas_df, persona_id, sector, type_org, omschrijving)
        st.success("Persona bijgewerkt.")

    st.markdown("---")
    _render_persona_matches(persona_id)


def _update_persona(
    personas_df: pd.DataFrame,
    persona_id: int,
    sector: str,
    type_org: str,
    omschrijving: str,
) -> None:
    idx = personas_df.index[personas_df["persona_id"] == persona_id]
    if len(idx) == 0:
        return
    i = idx[0]
    personas_df.at[i, "persona_sector"] = sector
    personas_df.at[i, "persona_organisatie_type"] = type_org
    personas_df.at[i, "persona_omschrijving"] = omschrijving

    set_table(PERSONAS_KEY, personas_df)


def _render_persona_matches(persona_id: int) -> None:
    st.markdown("### Matches voor deze persona")

    matches_df = get_table(MATCHES_KEY)
    subs_df = get_table(SUBSIDIES_KEY)

    persona_matches = matches_df[
        (matches_df["persona_id"] == persona_id)
        & (matches_df["type"] == "persona")
    ].copy()

    if persona_matches.empty:
        st.info("Geen matches gevonden voor deze persona.")
        return

    persona_matches = persona_matches.merge(
        subs_df[["subsidie_id", "subsidie_naam", "bron"]],
        how="left",
        on="subsidie_id",
    )

    persona_matches = persona_matches.sort_values("match_score", ascending=False)

    st.dataframe(
        persona_matches[
            [
                "match_id",
                "subsidie_naam",
                "bron",
                "match_score",
                "datum_toegevoegd",
            ]
        ],
        use_container_width=True,
    )


def _render_add_delete_persona(personas_df: pd.DataFrame) -> None:
    st.subheader("Nieuwe persona")

    with st.form("add_persona_form"):
        sector = st.text_input("Sector")
        type_org = st.text_input("Type organisatie")
        omschrijving = st.text_area("Omschrijving", height=120)
        submitted = st.form_submit_button("Toevoegen")

    if submitted and omschrijving:
        _add_persona(personas_df, sector, type_org, omschrijving)
        st.success("Persona toegevoegd.")

    st.subheader("Persona verwijderen")
    if not personas_df.empty:
        options = personas_df.copy()
        options["label"] = (
            options["persona_id"].astype(str)
            + " – "
            + options["persona_sector"]
            + " / "
            + options["persona_organisatie_type"]
        )
        selected_label = st.selectbox(
            "Te verwijderen persona",
            options=options["label"].tolist(),
            key="delete_persona_select",
        )
        row = options[options["label"] == selected_label].iloc[0]
        persona_id = int(row["persona_id"])

        if st.button("Verwijder persona"):
            _delete_persona(personas_df, persona_id)
            st.success("Persona verwijderd.")


def _add_persona(
    personas_df: pd.DataFrame,
    sector: str,
    type_org: str,
    omschrijving: str,
) -> None:
    new_id = next_id(PERSONAS_KEY, "persona_id")
    new_row = {
        "persona_id": new_id,
        "persona_sector": sector,
        "persona_organisatie_type": type_org,
        "persona_omschrijving": omschrijving,
    }
    new_df = pd.concat(
        [personas_df, pd.DataFrame([new_row])],
        ignore_index=True,
    )
    set_table(PERSONAS_KEY, new_df)


def _delete_persona(personas_df: pd.DataFrame, persona_id: int) -> None:
    new_df = personas_df[personas_df["persona_id"] != persona_id].copy()
    set_table(PERSONAS_KEY, new_df)
