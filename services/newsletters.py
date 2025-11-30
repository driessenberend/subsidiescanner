# services/newsletters.py
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd

from data.data_store import (
    MATCHES_KEY,
    NEWSLETTERS_KEY,
    ORGANISATIONS_KEY,
    SUBSIDIES_KEY,
    get_table,
    next_id,
    set_table,
)


def generate_newsletter_for_org(
    organisatie_id: int,
    weeks_back: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Genereer een nieuwsbrief voor een organisatie op basis van:
    - matches
    - subsidies met datum_toegevoegd binnen de afgelopen X weken
    - abonnement_type van de organisatie (stuurt standaard weeks_back)

    Retourneert het aangemaakte nieuwsbriefrecord als dict.
    """
    organisations_df = get_table(ORGANISATIONS_KEY)
    subsidies_df = get_table(SUBSIDIES_KEY)
    matches_df = get_table(MATCHES_KEY)
    newsletters_df = get_table(NEWSLETTERS_KEY)

    org_row = organisations_df.loc[organisations_df["organisatie_id"] == organisatie_id]
    if org_row.empty:
        raise ValueError(f"Organisatie met id {organisatie_id} niet gevonden.")

    org = org_row.iloc[0].to_dict()
    abonnement = org.get("abonnement_type", "basic")

    # Standaardlogica voor vensterbreedte per abonnement
    if weeks_back is None:
        if abonnement == "premium":
            weeks_back = 8
        else:
            weeks_back = 4

    today = datetime.today()
    start_date = today - timedelta(weeks=weeks_back)

    relevant_subsidies = subsidies_df[
        (subsidies_df["datum_toegevoegd"] >= pd.to_datetime(start_date))
        & (subsidies_df["datum_toegevoegd"] <= pd.to_datetime(today))
    ]

    if relevant_subsidies.empty:
        content = (
            f"Nieuwsbrief voor {org.get('organisatie_naam')} op {today.date()}.\n\n"
            "Er zijn geen nieuwe subsidies toegevoegd in de gekozen periode."
        )
        ranked = pd.DataFrame(columns=["subsidie_id", "match_score"])
    else:
        org_matches = matches_df[
            (matches_df["organisatie_id"] == organisatie_id)
            & (matches_df["subsidie_id"].isin(relevant_subsidies["subsidie_id"]))
            & (matches_df["type"] == "organisatie")
        ]

        if org_matches.empty:
            ranked = pd.DataFrame(columns=["subsidie_id", "match_score"])
        else:
            ranked = (
                org_matches[["subsidie_id", "match_score", "match_toelichting"]]
                .sort_values("match_score", ascending=False)
                .reset_index(drop=True)
            )

        content_lines = [
            f"Nieuwsbrief voor {org.get('organisatie_naam')} op {today.date()}",
            "",
            f"Periode: laatste {weeks_back} weken.",
            "",
        ]

        if ranked.empty:
            content_lines.append(
                "Er zijn wel subsidies toegevoegd, maar (nog) geen matches gevonden voor deze organisatie."
            )
        else:
            content_lines.append("Top-subsidies op basis van matchscore:")
            content_lines.append("")
            for _, row in ranked.iterrows():
                sub_row = relevant_subsidies[
                    relevant_subsidies["subsidie_id"] == row["subsidie_id"]
                ]
                if sub_row.empty:
                    continue
                sub = sub_row.iloc[0].to_dict()
                content_lines.append(
                    f"- {sub.get('subsidie_naam')} (bron: {sub.get('bron')}) – matchscore {int(row['match_score'])}"
                )
                content_lines.append(
                    f"  Voor wie: {sub.get('voor_wie', '')}".strip()
                )
                toelichting = str(row.get("match_toelichting", "")).replace("\n", " • ")
                if toelichting:
                    content_lines.append(f"  Toelichting: {toelichting}")
                content_lines.append(
                    f"  Link: {sub.get('weblink', '')}".strip()
                )
                content_lines.append("")

        content = "\n".join(content_lines)

    nieuwsbrief_id = next_id(NEWSLETTERS_KEY, "nieuwsbrief_id")

    new_row = {
        "nieuwsbrief_id": nieuwsbrief_id,
        "organisatie_id": organisatie_id,
        "organisatie_naam": org.get("organisatie_naam"),
        "nieuwsbrief_datum": today,
        "nieuwsbrief_content": content,
    }

    newsletters_df = pd.concat(
        [newsletters_df, pd.DataFrame([new_row])],
        ignore_index=True,
    )
    newsletters_df["nieuwsbrief_datum"] = pd.to_datetime(
        newsletters_df["nieuwsbrief_datum"]
    )

    set_table(NEWSLETTERS_KEY, newsletters_df)

    return new_row


def get_newsletters_for_org(organisatie_id: int) -> pd.DataFrame:
    """
    Geef alle nieuwsbrieven voor een organisatie, gesorteerd op datum aflopend.
    """
    newsletters_df = get_table(NEWSLETTERS_KEY)
    df = newsletters_df[newsletters_df["organisatie_id"] == organisatie_id].copy()
    if df.empty:
        return df
    return df.sort_values("nieuwsbrief_datum", ascending=False).reset_index(drop=True)
