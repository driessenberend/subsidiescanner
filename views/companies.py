# views/companies.py
import streamlit as st
import pandas as pd

from data.data_store import (
    MATCHES_KEY,
    ORGANISATIONS_KEY,
    SUBSIDIES_KEY,
    get_table,
    next_id,
    set_table,
)


def render_companies() -> None:
    st.title("Organisations")

    orgs_df = get_table(ORGANISATIONS_KEY).copy()

    st.subheader("Filters")
    filters = _render_filters(orgs_df)
    filtered = _apply_filters(orgs_df, filters)

    st.subheader("Overzicht organisaties")
    st.dataframe(
        filtered[
            [
                "organisatie_id",
                "organisatie_naam",
                "abonnement_type",
                "sector",
                "type_organisatie",
                "locatie",
                "aantal_medewerkers",
                "omzet",
            ]
        ].sort_values("organisatie_id"),
        use_container_width=True,
    )

    st.markdown("---")
    _render_org_detail(orgs_df)

    st.markdown("---")
    _render_add_delete_org(orgs_df)


def _render_filters(df: pd.DataFrame) -> dict:
    col_sector, col_type, col_search = st.columns([1, 1, 2])

    with col_sector:
        sectors = ["Alle"] + sorted(df["sector"].dropna().unique().tolist())
        sector_filter = st.selectbox("Sector", sectors)

    with col_type:
        types = ["Alle"] + sorted(
            df["type_organisatie"].dropna().unique().tolist()
        )
        type_filter = st.selectbox("Type organisatie", types)

    with col_search:
        search_text = st.text_input("Zoek op naam of locatie", "")

    return {
        "sector_filter": sector_filter,
        "type_filter": type_filter,
        "search_text": search_text.strip().lower(),
    }


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df.copy()

    if filters["sector_filter"] != "Alle":
        out = out[out["sector"] == filters["sector_filter"]]

    if filters["type_filter"] != "Alle":
        out = out[out["type_organisatie"] == filters["type_filter"]]

    if filters["search_text"]:
        text = filters["search_text"]
        mask = (
            out["organisatie_naam"].str.lower().str.contains(text)
            | out["locatie"].str.lower().str.contains(text)
        )
        out = out[mask]

    return out


def _render_org_detail(orgs_df: pd.DataFrame) -> None:
    st.subheader("Detailorganisatie")

    if orgs_df.empty:
        st.info("Geen organisaties beschikbaar.")
        return

    options = orgs_df.copy()
    options["label"] = (
        options["organisatie_id"].astype(str)
        + " – "
        + options["organisatie_naam"]
    )

    selected_label = st.selectbox(
        "Kies organisatie",
        options=options["label"].tolist(),
    )
    org_row = options[options["label"] == selected_label].iloc[0]
    org_id = int(org_row["organisatie_id"])

    with st.form(key=f"org_edit_form_{org_id}"):
        st.markdown("**Basisgegevens**")
        naam = st.text_input(
            "Naam",
            value=org_row["organisatie_naam"],
        )
        abonnement_type = st.selectbox(
            "Abonnement",
            options=["basic", "premium"],
            index=["basic", "premium"].index(org_row["abonnement_type"]),
        )
        sector = st.text_input(
            "Sector",
            value=org_row["sector"],
        )
        type_org = st.text_input(
            "Type organisatie",
            value=org_row["type_organisatie"],
        )
        locatie = st.text_input("Locatie", value=org_row["locatie"])
        omzet = st.number_input(
            "Omzet",
            value=float(org_row["omzet"]),
            min_value=0.0,
            step=100000.0,
        )
        aantal_medewerkers = st.number_input(
            "Aantal medewerkers",
            value=int(org_row["aantal_medewerkers"]),
            min_value=0,
            step=1,
        )
        website = st.text_input(
            "Website",
            value=org_row["website_link"],
        )

        st.markdown("**Organisatieprofiel**")
        profiel = st.text_area(
            "Omschrijving",
            value=org_row["organisatieprofiel"],
            height=150,
        )

        submitted = st.form_submit_button("Opslaan wijzigingen")

    if submitted:
        _update_org(
            orgs_df,
            org_id,
            naam,
            abonnement_type,
            sector,
            type_org,
            locatie,
            omzet,
            aantal_medewerkers,
            website,
            profiel,
        )
        st.success("Organisatie bijgewerkt.")

    st.markdown("### Matches voor deze organisatie")

    matches_df = get_table(MATCHES_KEY)
    subs_df = get_table(SUBSIDIES_KEY)

    org_matches = matches_df[
        (matches_df["organisatie_id"] == org_id)
        & (matches_df["type"] == "organisatie")
    ].copy()

    if org_matches.empty:
        st.info("Geen matches gevonden voor deze organisatie.")
    else:
        org_matches = org_matches.merge(
            subs_df[["subsidie_id", "subsidie_naam", "bron"]],
            how="left",
            on="subsidie_id",
        )
        org_matches = org_matches.sort_values("match_score", ascending=False)
        st.dataframe(
            org_matches[
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


def _update_org(
    orgs_df: pd.DataFrame,
    org_id: int,
    naam: str,
    abonnement_type: str,
    sector: str,
    type_org: str,
    locatie: str,
    omzet: float,
    aantal_medewerkers: int,
    website: str,
    profiel: str,
) -> None:
    idx = orgs_df.index[orgs_df["organisatie_id"] == org_id]
    if len(idx) == 0:
        return

    i = idx[0]
    orgs_df.at[i, "organisatie_naam"] = naam
    orgs_df.at[i, "abonnement_type"] = abonnement_type
    orgs_df.at[i, "sector"] = sector
    orgs_df.at[i, "type_organisatie"] = type_org
    orgs_df.at[i, "locatie"] = locatie
    orgs_df.at[i, "omzet"] = omzet
    orgs_df.at[i, "aantal_medewerkers"] = aantal_medewerkers
    orgs_df.at[i, "website_link"] = website
    orgs_df.at[i, "organisatieprofiel"] = profiel

    set_table(ORGANISATIONS_KEY, orgs_df)


def _render_add_delete_org(orgs_df: pd.DataFrame) -> None:
    st.subheader("Nieuwe organisatie")

    with st.form("add_org_form"):
        naam = st.text_input("Naam nieuwe organisatie")
        abonnement_type = st.selectbox(
            "Abonnement",
            options=["basic", "premium"],
        )
        sector = st.text_input("Sector")
        type_org = st.text_input("Type organisatie")
        locatie = st.text_input("Locatie")
        omzet = st.number_input(
            "Omzet",
            min_value=0.0,
            step=100000.0,
        )
        aantal_medewerkers = st.number_input(
            "Aantal medewerkers",
            min_value=0,
            step=1,
        )
        website = st.text_input("Website")
        profiel = st.text_area(
            "Organisatieprofiel",
            height=120,
        )

        submitted = st.form_submit_button("Toevoegen")

    if submitted and naam:
        _add_org(
            orgs_df,
            naam,
            abonnement_type,
            sector,
            type_org,
            locatie,
            omzet,
            aantal_medewerkers,
            website,
            profiel,
        )
        st.success("Organisatie toegevoegd.")

    st.subheader("Organisatie verwijderen")
    if not orgs_df.empty:
        options = orgs_df.copy()
        options["label"] = (
            options["organisatie_id"].astype(str)
            + " – "
            + options["organisatie_naam"]
        )
        selected_label = st.selectbox(
            "Te verwijderen organisatie",
            options=options["label"].tolist(),
            key="delete_org_select",
        )
        org_row = options[options["label"] == selected_label].iloc[0]
        org_id = int(org_row["organisatie_id"])

        if st.button("Verwijder organisatie"):
            _delete_org(orgs_df, org_id)
            st.success("Organisatie verwijderd.")


def _add_org(
    orgs_df: pd.DataFrame,
    naam: str,
    abonnement_type: str,
    sector: str,
    type_org: str,
    locatie: str,
    omzet: float,
    aantal_medewerkers: int,
    website: str,
    profiel: str,
) -> None:
    new_id = next_id(ORGANISATIONS_KEY, "organisatie_id")
    new_row = {
        "organisatie_id": new_id,
        "organisatie_naam": naam,
        "abonnement_type": abonnement_type,
        "sector": sector,
        "type_organisatie": type_org,
        "omzet": omzet,
        "aantal_medewerkers": aantal_medewerkers,
        "locatie": locatie,
        "organisatieprofiel": profiel,
        "website_link": website,
    }

    new_df = pd.concat(
        [orgs_df, pd.DataFrame([new_row])],
        ignore_index=True,
    )
    set_table(ORGANISATIONS_KEY, new_df)


def _delete_org(orgs_df: pd.DataFrame, org_id: int) -> None:
    new_df = orgs_df[orgs_df["organisatie_id"] != org_id].copy()
    set_table(ORGANISATIONS_KEY, new_df)
