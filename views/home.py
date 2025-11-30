# views/home.py
import streamlit as st

from data.data_store import get_active_prompt, get_table, PROMPTS_KEY
from services.matching import recompute_all_matches, update_prompt_template
from services.llm_client import get_llm_client


def render_home() -> None:
    st.title("Subsidiematch")

    _render_intro()
    st.markdown("---")
    _render_flow_overview()
    st.markdown("---")
    _render_prompt_editor()
    st.markdown("---")
    _render_dataset_overview()


def _render_intro() -> None:
    st.subheader("Wat doet deze applicatie?")

    st.markdown(
        """
Subsidiematch helpt bepalen welke subsidies relevant zijn voor organisaties en persona’s:

- Organisaties en persona’s worden beschreven met een profiel.
- Subsidies hebben een set kenmerken (doelgroep, eisen, bedragen).
- Een LLM (of mock-logica) beoordeelt de fit en geeft een **matchscore (1–100)** en korte toelichting.
- Resultaten worden opgeslagen in de tabel **Matches** en gebruikt voor o.a. nieuwsbrieven.
        """
    )


def _render_flow_overview() -> None:
    st.subheader("Hoe komen matches tot stand?")

    st.markdown(
        """
Globale stappen:

1. **Data-ingang**
   - Organisaties, subsidies en persona’s worden vastgelegd in tabellen.
2. **Matching**
   - Voor elke organisatie/persona × subsidie wordt een prompt opgebouwd.
   - De prompt gaat naar een LLM of, zonder API-key, naar een mock-functie.
3. **Resultaat**
   - Per combinatie ontstaat een matchscore (1–100) plus toelichting.
   - Deze wordt als rij in **Matches** opgeslagen.
4. **Gebruik**
   - Overzicht van beste matches per organisatie/persona.
   - Samenstellen van nieuwsbrieven per organisatie.
        """
    )

    with st.expander("Visuele flow (vereenvoudigd)", expanded=False):
        st.graphviz_chart(
            """
digraph G {
    rankdir=LR;

    subgraph cluster_org {
        label="Organisaties & Persona's";
        style=dashed;
        orgs [label="Organisaties"];
        personas [label="Persona's"];
    }

    subsidies [label="Subsidies"];
    prompt [label="Prompt-template"];
    llm [label="LLM / mock"];
    matches [label="Matches"];
    newsletters [label="Nieuwsbrieven"];

    orgs -> prompt;
    personas -> prompt;
    subsidies -> prompt;
    prompt -> llm;
    llm -> matches;
    matches -> newsletters;
}
            """
        )


def _render_prompt_editor() -> None:
    st.subheader("Prompt voor matching")

    active = get_active_prompt()
    if active is None:
        st.warning("Geen actieve prompt gevonden.")
        return

    llm_client = get_llm_client()
    if llm_client.is_real():
        st.info(
            "Er is een OPENAI_API_KEY geconfigureerd. Matches gebruiken de echte LLM backend."
        )
    else:
        st.info(
            "Er is geen OPENAI_API_KEY gevonden. Matches gebruiken een mock-algoritme (demo-modus)."
        )

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"**Actieve prompt:** {active.get('naam', 'Onbekend')} "
            f"(id: {active.get('prompt_id')})"
        )
    with col2:
        st.caption(
            f"Laatst gewijzigd: {active.get('laatst_gewijzigd')}"
        )

    current_template = active.get("prompt_template", "")

    new_template = st.text_area(
        label="Prompt-template",
        value=current_template,
        height=300,
        help="Gebruik placeholders zoals {organisatieprofiel}, {subsidie_naam}, {bron}, {voor_wie}, {samenvatting_eisen}.",
    )

    col_save, col_recompute = st.columns([1, 2])

    with col_save:
        if st.button("Prompt opslaan"):
            update_prompt_template(new_template)
            st.success("Prompt opgeslagen.")

    with col_recompute:
        if st.button("Alle matches opnieuw berekenen"):
            with st.spinner("Matches worden opnieuw berekend..."):
                recompute_all_matches()
            st.success("Matches opnieuw berekend.")


def _render_dataset_overview() -> None:
    st.subheader("Overzicht van tabellen")

    prompts_df = get_table(PROMPTS_KEY)
    st.markdown(
        """
De applicatie gebruikt in-memory tabellen (DataFrames) voor:

- **Organisations**: bedrijven / instellingen
- **Subsidies**: beschikbare regelingen
- **Personas**: rollen / archetypes binnen organisaties
- **Matches**: berekende combinaties met scores
- **Newsletters**: gegenereerde nieuwsbrieven per organisatie
- **Prompts**: gebruikte prompt-templates voor matching
        """
    )

    with st.expander("Prompts-tabel (read-only overzicht)", expanded=False):
        st.dataframe(
            prompts_df[
                ["prompt_id", "naam", "laatst_gewijzigd", "actief"]
            ].sort_values("prompt_id"),
            use_container_width=True,
        )
