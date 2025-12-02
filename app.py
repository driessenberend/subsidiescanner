import streamlit as st

from data.data_store import init_session_state

import views.home as home
import views.matches as matches
import views.companies as companies
import views.subsidies as subsidies



def configure_page() -> None:
    """Set global Streamlit page config."""
    st.set_page_config(
        page_title="Subsidiematch",
        page_icon="💶",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_sidebar() -> str:
    """
    Render the sidebar navigation and return the selected page key.
    """
    st.sidebar.title("Subsidiematch")

    st.sidebar.markdown("### Navigatie")

    page = st.sidebar.radio(
        label="Ga naar",
        options=[
            "Home",
            "Matches",
            "Organisations",
            "Subsidies",
        ],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Proof of Concept – data is in-memory en wordt gewist bij herstart."
    )

    return page


def main() -> None:
    configure_page()

    # Initialise in-memory dataframes and other session state
    init_session_state()

    page = render_sidebar()

    # Router over de tabbladen
    if page == "Home":
        home.render_home()
    elif page == "Matches":
        matches.render_matches()
    elif page == "Organisations":
        companies.render_companies()
    elif page == "Subsidies":
        subsidies.render_subsidies()
    else:
        st.error("Onbekende pagina-selectie.")



if __name__ == "__main__":
    main()
