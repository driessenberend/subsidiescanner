# views/subsidies.py
import streamlit as st
import pandas as pd

from data.data_store import (
    MATCHES_KEY,
    ORGANISATIONS_KEY,
    PERSONAS_KEY,
    SUBSIDIES_KEY,
    get_table,
    next_id,
    set_table,
)


def render_subsidies() -> None:
    st.title("Subsidies")

    subs_df = get_table(SUBSIDIES_KEY).copy()

    st.subheader("Filters")
    filters = _render_filters(subs_df)
    filtered = _apply_filters(subs_df, filters)

    st.subheader("Overzicht subsidies")
    st.dataframe(
        filtered[
            [
                "subsidie_id",
                "subsidie_naam",
                "bron",
                "datum_toegevoegd",
                "sluitingsdatum",
                "subsidiebedrag",
            ]
        ].sort_values("subsidie_id"),
        use_container_width=True,
    )

    st.markdown("---")
    cols = st.columns([2, 1])
    with cols[0]:
        _render_subsidie_detail(subs_df)
    with cols[1]:
        _render_add_subsidie(subs_df)


def _render_filters(df: pd.DataFrame) -> dict:
    col_bron, col_date, col_search = st.columns([1, 1.2, 2])

    with col_bron:
        bronnen = ["Alle"] + sorted(df["bron"].dropna().unique().tolist())
        bron_filter = st.selectbox("Bron", bronnen)

    with col_date:
        min_date = df["sluitingsdatum"].min().date() if not df.empty else None
        max_date = df["sluitingsdatum"].max().date() if not df.empty else None
        if min_date and max_date:
            date_range = st.date_input(
                "Sluitingsdatum tussen",
                value=(min_date, max_date),
            )
        else:
            date_range = None

    with col_search:
        search_text = st.text_input(
            "Zoek in naam of 'voor wie'",
            "",
        )

    return {
        "bron_filter": bron_filter,
        "date_range": date_range,
        "search_text": search_text.strip().lower(),
    }


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df.copy()

    if filters["bron_filter"] != "Alle":
        out = out[out["bron"] == filters["bron_filter"]]

    if filters["date_range"] and isinstance(filters["date_range"], tuple):
        start, end = filters["date_range"]
        if start and end:
            out = out[
                (out["sluitingsdatum"].dt.date >= start)
                & (out["sluitingsdatum"].dt.date <= end)
            ]

    if filters["search_text"]:
        text = filters["search_text"]
        mask = (
            out["subsidie_naam"].str.lower().str.contains(text)
            | out["voor_wie"].str.lower().str.contains(text)
        )
        out = out[mask]

    return out


def _render_subsidie_detail(subs_df: pd.DataFrame) -> None:
    st.subheader("Details subsidie")

    if subs_df.empty:
        st.info("Geen subsidies beschikbaar.")
        return

    options = subs_df.copy()
    options["label"] = (
        options["subsidie_id"].astype(str)
        + " – "
        + options["subsidie_naam"]
    )

    selected_label = st.selectbox(
        "Kies subsidie",
        options=options["label"].tolist(),
    )
    row = options[options["label"] == selected_label].iloc[0]
    sub_id = int(row["subsidie_id"])

    with st.form(key=f"sub_edit_form_{sub_id}"):
        naam = st.text_input(
            "Naam",
            value=row["subsidie_naam"],
        )
        bron = st.text_input(
            "Bron",
            value=row["bron"],
        )
        datum_toegevoegd = st.date_input(
            "Datum toegevoegd",
            value=row["datum_toegevoegd"].date(),
        )
        sluitingsdatum = st.date_input(
            "Sluitingsdatum",
            value=row["sluitingsdatum"].date(),
        )
        bedrag = st.text_input(
            "Subsidiebedrag",
            value=row["subsidiebedrag"],
        )
        voor_wie = st.text_area(
            "Voor wie",
            value=row["voor_wie"],
            height=100,
        )
        eisen = st.text_area(
            "Samenvatting eisen",
            value=row["samenvatting_eisen"],
            height=120,
        )
        weblink = st.text_input(
            "Weblink",
            value=row["weblink"],
        )

        submitted = st.form_submit_button("Opslaan wijzigingen")

    if submitted:
        _update_subsidie(
            subs_df,
            sub_id,
            naam,
            bron,
            datum_toegevoegd,
            sluitingsdatum,
            bedrag,
            voor_wie,
            eisen,
            weblink,
        )
        st.success("Subsidie bijgewerkt.")

    st.markdown("---")
    _render_subsidie_matches(sub_id)


def _update_subsidie(
    subs_df: pd.DataFrame,
    sub_id: int,
    naam: str,
    bron: str,
    datum_toegevoegd,
    sluitingsdatum,
    bedrag: str,
    voor_wie: str,
    eisen: str,
    weblink: str,
) -> None:
    idx = subs_df.index[subs_df["subsidie_id"] == sub_id]
    if len(idx) == 0:
        return
    i = idx[0]
    subs_df.at[i, "subsidie_naam"] = naam
    subs_df.at[i, "bron"] = bron
    subs_df.at[i, "datum_toegevoegd"] = pd.to_datetime(datum_toegevoegd)
    subs_df.at[i, "sluitingsdatum"] = pd.to_datetime(sluitingsdatum)
    subs_df.at[i, "subsidiebedrag"] = bedrag
    subs_df.at[i, "voor_wie"] = voor_wie
    subs_df.at[i, "samenvatting_eisen"] = eisen
    subs_df.at[i, "weblink"] = weblink

    set_table(SUBSIDIES_KEY, subs_df)


def _render_subsidie_matches(sub_id: int) -> None:
    st.markdown("### Matches voor deze subsidie")

    matches_df = get_table(MATCHES_KEY)
    orgs_df = get_table(ORGANISATIONS_KEY)
    personas_df = get_table(PERSONAS_KEY)

    subs_matches = matches_df[matches_df["subsidie_id"] == sub_id].copy()
    if subs_matches.empty:
        st.info("Geen matches gevonden voor deze subsidie.")
        return

    orgs_df = orgs_df.rename(
        columns={"organisatie_naam": "org_naam"}
    )
    personas_df = personas_df.copy()
    personas_df["persona_label"] = (
        personas_df["persona_id"].astype(str)
        + " – "
        + personas_df["persona_sector"].fillna("")
        + " / "
        + personas_df["persona_organisatie_type"].fillna("")
    )

    subs_matches = subs_matches.merge(
        orgs_df[["organisatie_id", "org_naam"]],
        how="left",
        on="organisatie_id",
    )
    subs_matches = subs_matches.merge(
        personas_df[["persona_id", "persona_label"]],
        how="left",
        on="persona_id",
    )

    subs_matches = subs_matches.sort_values("match_score", ascending=False)

    st.dataframe(
        subs_matches[
            [
                "match_id",
                "type",
                "match_score",
                "org_naam",
                "persona_label",
                "datum_toegevoegd",
            ]
        ],
        use_container_width=True,
    )


def _render_add_subsidie(subs_df: pd.DataFrame) -> None:
    st.subheader("Nieuwe subsidie")

    with st.form("add_subsidie_form"):
        naam = st.text_input("Naam")
        bron = st.text_input("Bron")
        datum_toegevoegd = st.date_input("Datum toegevoegd")
        sluitingsdatum = st.date_input("Sluitingsdatum")
        bedrag = st.text_input("Subsidiebedrag")
        voor_wie = st.text_area("Voor wie", height=80)
        eisen = st.text_area("Samenvatting eisen", height=100)
        weblink = st.text_input("Weblink")

        submitted = st.form_submit_button("Toevoegen")

    if submitted and naam:
        _add_subsidie(
            subs_df,
            naam,
            bron,
            datum_toegevoegd,
            sluitingsdatum,
            bedrag,
            voor_wie,
            eisen,
            weblink,
        )
        st.success("Subsidie toegevoegd.")


def _add_subsidie(
    subs_df: pd.DataFrame,
    naam: str,
    bron: str,
    datum_toegevoegd,
    sluitingsdatum,
    bedrag: str,
    voor_wie: str,
    eisen: str,
    weblink: str,
) -> None:
    new_id = next_id(SUBSIDIES_KEY, "subsidie_id")
    new_row = {
        "subsidie_id": new_id,
        "subsidie_naam": naam,
        "bron": bron,
        "datum_toegevoegd": pd.to_datetime(datum_toegevoegd),
        "sluitingsdatum": pd.to_datetime(sluitingsdatum),
        "subsidiebedrag": bedrag,
        "voor_wie": voor_wie,
        "samenvatting_eisen": eisen,
        "weblink": weblink,
    }
    new_df = pd.concat(
        [subs_df, pd.DataFrame([new_row])],
        ignore_index=True,
    )
    set_table(SUBSIDIES_KEY, new_df)
