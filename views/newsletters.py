# views/newsletters.py
import streamlit as st
import pandas as pd

from data.data_store import (
    NEWSLETTERS_KEY,
    ORGANISATIONS_KEY,
    get_table,
)
from services.newsletters import generate_newsletter_for_org


def render_newsletters() -> None:
    st.title("Newsletters")

    newsletters_df = get_table(NEWSLETTERS_KEY).copy()
    orgs_df = get_table(ORGANISATIONS_KEY)

    st.subheader("Filters")

    col_org, col_search = st.columns([1, 2])

    with col_org:
        org_options = ["Alle"] + [
            f"{row['organisatie_id']} – {row['organisatie_naam']}"
            for _, row in orgs_df.iterrows()
        ]
        org_choice = st.selectbox("Organisatie", org_options)

    with col_search:
        search_text = st.text_input("Zoek in inhoud", "")

    filtered = _apply_filters(newsletters_df, org_choice, search_text.strip().lower())

    st.subheader("Overzicht nieuwsbrieven")
    if filtered.empty:
        st.info("Geen nieuwsbrieven beschikbaar.")
    else:
        st.dataframe(
            filtered[
                [
                    "nieuwsbrief_id",
                    "nieuwsbrief_datum",
                    "organisatie_naam",
                ]
            ].sort_values("nieuwsbrief_datum", ascending=False),
            use_container_width=True,
        )

        st.markdown("---")
        _render_detail(filtered)

    st.markdown("---")
    _render_generate_from_tab(orgs_df)


def _apply_filters(
    df: pd.DataFrame,
    org_choice: str,
    search_text: str,
) -> pd.DataFrame:
    out = df.copy()
    if out.empty:
        return out

    if org_choice != "Alle":
        org_id_str = org_choice.split(" – ")[0]
        try:
            org_id = int(org_id_str)
            out = out[out["organisatie_id"] == org_id]
        except ValueError:
            pass

    if search_text:
        mask = out["nieuwsbrief_content"].str.lower().str.contains(search_text)
        out = out[mask]

    if "nieuwsbrief_datum" in out.columns:
        out["nieuwsbrief_datum"] = pd.to_datetime(out["nieuwsbrief_datum"])

    return out


def _render_detail(df: pd.DataFrame) -> None:
    st.subheader("Detail nieuwsbrief")

    options = df.sort_values("nieuwsbrief_datum", ascending=False)
    options["label"] = (
        options["nieuwsbrief_id"].astype(str)
        + " – "
        + options["organisatie_naam"]
        + " – "
        + options["nieuwsbrief_datum"].dt.strftime("%Y-%m-%d")
    )

    selected_label = st.selectbox(
        "Kies nieuwsbrief",
        options=options["label"].tolist(),
    )
    row = options[options["label"] == selected_label].iloc[0]

    st.markdown(
        f"**Nieuwsbrief {row['nieuwsbrief_id']} voor {row['organisatie_naam']}**"
    )
    st.write(f"Datum: {row['nieuwsbrief_datum'].date()}")

    st.markdown("**Inhoud**")
    st.text(row["nieuwsbrief_content"])


def _render_generate_from_tab(orgs_df: pd.DataFrame) -> None:
    st.subheader("Nieuwsbrief genereren")

    if orgs_df.empty:
        st.info("Geen organisaties beschikbaar om een nieuwsbrief voor te genereren.")
        return

    options = orgs_df.copy()
    options["label"] = (
        options["organisatie_id"].astype(str)
        + " – "
        + options["organisatie_naam"]
    )
    selected_label = st.selectbox(
        "Organisatie voor nieuwsbrief",
        options=options["label"].tolist(),
        key="news_gen_org_select",
    )
    row = options[options["label"] == selected_label].iloc[0]
    org_id = int(row["organisatie_id"])

    weeks_back = st.number_input(
        "Aantal weken terug",
        min_value=1,
        max_value=52,
        value=4,
        step=1,
        help="Laat leeg om automatisch te bepalen aan de hand van het abonnementstype.",
    )

    if st.button("Genereer nieuwsbrief"):
        weeks_arg = int(weeks_back) if weeks_back else None
        new_newsletter = generate_newsletter_for_org(org_id, weeks_back=weeks_arg)
        st.success(
            f"Nieuwsbrief aangemaakt (id {new_newsletter['nieuwsbrief_id']})."
        )
