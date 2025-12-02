# views/matches.py
import streamlit as st
import pandas as pd

from data.data_store import (
    MATCHES_KEY,
    ORGANISATIONS_KEY,
    SUBSIDIES_KEY,
    get_table,
)


def render_matches() -> None:
    st.title("Matches")

    matches_df = get_table(MATCHES_KEY).copy()
    orgs_df = get_table(ORGANISATIONS_KEY)
    subs_df = get_table(SUBSIDIES_KEY)

    if matches_df.empty:
        st.info("Er zijn nog geen matches beschikbaar. Genereer matches met AI via het tabblad 'Home'.")
        return

    matches_df = _enrich_matches(matches_df, orgs_df, subs_df)

    filters = _render_filters(matches_df)
    filtered = _apply_filters(matches_df, filters)

    st.subheader("Overzicht matches")
    st.dataframe(
        filtered[
            [
                "match_id",
                "type",
                "match_score",
                "organisatie_naam",
                "subsidie_naam",
                "bron",
                "datum_toegevoegd",
            ]
        ].sort_values("match_score", ascending=False),
        use_container_width=True,
    )

    st.markdown("---")
    _render_match_detail(filtered)


def _enrich_matches(
    matches_df: pd.DataFrame,
    orgs_df: pd.DataFrame,
    subs_df: pd.DataFrame,
) -> pd.DataFrame:
    df = matches_df.copy()

    # Normaliseer typen voor IDs om merge-fouten te voorkomen
    if "organisatie_id" in df.columns:
        df["organisatie_id"] = pd.to_numeric(df["organisatie_id"], errors="coerce").astype("Int64")
    if "subsidie_id" in df.columns:
        df["subsidie_id"] = pd.to_numeric(df["subsidie_id"], errors="coerce").astype("Int64")

    orgs_df = orgs_df.copy()
    subs_df = subs_df.copy()

    if "organisatie_id" in orgs_df.columns:
        orgs_df["organisatie_id"] = pd.to_numeric(
            orgs_df["organisatie_id"], errors="coerce"
        ).astype("Int64")

    if "subsidie_id" in subs_df.columns:
        subs_df["subsidie_id"] = pd.to_numeric(
            subs_df["subsidie_id"], errors="coerce"
        ).astype("Int64")

    # Organisatienaam erbij
    df = df.merge(
        orgs_df[["organisatie_id", "organisatie_naam"]],
        how="left",
        on="organisatie_id",
    )

    # Subsidie-info erbij
    df = df.merge(
        subs_df[["subsidie_id", "subsidie_naam", "bron"]],
        how="left",
        on="subsidie_id",
    )

    if "datum_toegevoegd" in df.columns:
        df["datum_toegevoegd"] = pd.to_datetime(df["datum_toegevoegd"]).dt.date

    return df


def _render_filters(df: pd.DataFrame) -> dict:
    st.subheader("Filters")

    col_type, col_min_score, col_search = st.columns([1, 1, 2])

    with col_type:
        type_filter = st.selectbox(
            "Type",
            options=["Alle", "organisatie", "persona"],
        )

    with col_min_score:
        min_score = st.slider(
            "Minimale matchscore",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
        )

    with col_search:
        search_text = st.text_input(
            "Zoek in organisatie- of subsidienaam",
            value="",
        )

    return {
        "type_filter": type_filter,
        "min_score": min_score,
        "search_text": search_text.strip().lower(),
    }


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df.copy()

    if filters["type_filter"] != "Alle":
        out = out[out["type"] == filters["type_filter"]]

    out = out[out["match_score"] >= filters["min_score"]]

    if filters["search_text"]:
        text = filters["search_text"]
        mask = (
            out["organisatie_naam"].fillna("").str.lower().str.contains(text)
            | out["subsidie_naam"].fillna("").str.lower().str.contains(text)
        )
        out = out[mask]

    return out


def _render_match_detail(df: pd.DataFrame) -> None:
    st.subheader("Detail van een match")

    if df.empty:
        st.info("Geen matches na filteren.")
        return

    options = df.sort_values("match_score", ascending=False)
    options["label"] = (
        options["match_id"].astype(str)
        + " – "
        + options["type"]
        + " – "
        + options["subsidie_naam"].fillna("")
        + " – score "
        + options["match_score"].astype(str)
    )

    selected_label = st.selectbox(
        "Selecteer een match",
        options=options["label"].tolist(),
    )

    selected_row = options[options["label"] == selected_label].iloc[0]

    st.markdown("### Gekozen match")

    cols = st.columns(3)
    with cols[0]:
        st.metric("Matchscore", int(selected_row["match_score"]))
    with cols[1]:
        st.write("**Organisatie**")
        st.write(selected_row.get("organisatie_naam") or "–")

    st.markdown("**Subsidie**")
    st.write(selected_row.get("subsidie_naam") or "Onbekend")
    st.write(f"Bron: {selected_row.get('bron') or 'Onbekend'}")

    st.markdown("**Toelichting**")
    st.text(selected_row.get("match_toelichting") or "")

    st.markdown("**Datum toegevoegd**")
    st.write(selected_row.get("datum_toegevoegd"))

