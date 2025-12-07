# views/home.py
import streamlit as st

from data.data_store import get_active_prompt, get_table, PROMPTS_KEY, MATCHES_KEY
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
Subsidiematch helpt bepalen welke subsidies relevant zijn voor organisaties:

- Organisaties worden vastgelegd met basiskenmerken en een tekstueel profiel.
- Subsidies hebben kenmerken zoals bron, doelgroep, eisen en subsidiebedrag.
- Een LLM (of mock-logica) beoordeelt per organisatie–subsidie-combinatie de fit.
- Het resultaat is een **matchscore (1–100)** plus een korte toelichting.
- Alle uitkomsten komen in de tabel **Matches** en zijn zichtbaar op het tabblad *Matches*.

Je kunt in deze PoC:
- organisaties bekijken, aanpassen, toevoegen en verwijderen (tab *Organisations*);
- subsidies bekijken, aanpassen, toevoegen en verwijderen (tab *Subsidies*);
- alle matches bekijken en filteren (tab *Matches*);
- de prompt aanpassen waarmee de LLM de matchscore bepaalt (hier op *Home*), en daarna alle matches opnieuw laten berekenen.
        """
    )


def _render_flow_overview() -> None:
    st.subheader("Hoe komen matches tot stand?")

    st.markdown(
        """
Globale stappen in deze vereenvoudigde versie:

1. **Input**
   - Organisaties: naam, type, sector, locatie, profieltekst.
   - Subsidies: naam, bron, voor wie, eisen, sluitingsdatum, bedrag.
2. **Promptopbouw**
   - Voor elke organisatie–subsidie-combinatie wordt een prompt opgebouwd op basis van het actieve prompt-template.
3. **Beoordeling**
   - De prompt gaat naar een LLM (of mock-algoritme als er geen API-key is).
   - De LLM retourneert een matchscore (1–100) en een korte toelichting.
4. **Opslag**
   - Resultaat wordt als rij in de tabel **Matches** opgeslagen.
5. **Analyse**
   - In het tabblad *Matches* filter en sorteer je de combinaties op score en bekijk je de toelichting.
        """
    )

    with st.expander("Visuele flow (vereenvoudigd)", expanded=False):
        st.graphviz_chart(
            """
digraph G {
    rankdir=LR;

    orgs        [label="Organisations"];
    subsidies   [label="Subsidies"];
    prompt      [label="Prompt-template"];
    llm         [label="LLM / mock"];
    matches     [label="Matches"];

    orgs -> prompt;
    subsidies -> prompt;
    prompt -> llm;
    llm -> matches;
}
            """
        )


def _render_prompt_editor() -> None:
    st.subheader("Prompt voor matching")

    active = get_active_prompt()
    if active is None:
        st.warning("Er is geen actieve prompt gevonden.")
        return

    llm_client = get_llm_client()
    if llm_client.is_real():
        st.info(
            "Er is een OPENAI_API_KEY geconfigureerd. Matches gebruiken de echte LLM-backend."
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
        help=(
            "Gebruik placeholders zoals {organisatieprofiel}, {subsidie_naam}, {bron}, "
            "{voor_wie}, {samenvatting_eisen}."
        ),
    )

    # Bepaal of er al matches bestaan
    matches_df = get_table(MATCHES_KEY)
    has_matches = not matches_df.empty
    button_label = "Alle matches opnieuw berekenen" if has_matches else "Genereer matches"

    col_save, col_recompute = st.columns([1, 2])

    with col_save:
        if st.button("Prompt opslaan"):
            update_prompt_template(new_template)
            st.success("Prompt opgeslagen.")

    with col_recompute:
        if st.button(button_label):
            with st.spinner("Matches worden berekend..."):
                recompute_all_matches()
            st.success("Matches zijn bijgewerkt.")

def _render_dataset_overview() -> None:
    st.subheader("Overzicht van tabellen in deze PoC")

    st.markdown(
        """
Deze applicatie gebruikt in-memory tabellen (pandas DataFrames) in `st.session_state`:

- **Organisations**  
  Basisgegevens van organisaties en hun profieltekst.

- **Subsidies**  
  Beschikbare regelingen met bron, doelgroep, eisen, bedragen en volledige tekst.

- **Matches**  
  Resultaten per organisatie–subsidie-combinatie: matchscore, toelichting, datum.

- **Prompts**  
  Prompt-templates die bepalen hoe de LLM de match beoordeelt.

De data leeft alleen in het geheugen: bij herstart van de app wordt de seed-data opnieuw geladen.
        """
    )