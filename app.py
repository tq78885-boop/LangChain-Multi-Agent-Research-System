import streamlit as st
from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


def run_research_pipeline(topic: str) -> dict:
    state = {}

    # step 1 - search agent
    with st.spinner("Step 1: Search agent is working..."):
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [
                ("user", f"Find recent, reliable and detailed information about: {topic}")
            ]
        })
    state["search_results"] = search_result["messages"][-1].content

    # step 2 - reader agent
    with st.spinner("Step 2: Reader agent is working..."):
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [
                ("user",
                 f"Based on the following search results about '{topic}',"
                 f"pick the most relevant URL and scrape it for deeper content. \n\n"
                 f"Search Results:\n{state['search_results'][:800]}")
            ]
        })
    state["scraped_content"] = reader_result["messages"][-1].content

    # step 3 - writer chain
    with st.spinner("Step 3: Writer is drafting the report..."):
        research_combined = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
        )
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        })

    # step 4 - critic chain
    with st.spinner("Step 4: Critic is evaluating the report..."):
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })

    return state


st.set_page_config(page_title="Research Pipeline", page_icon="🔍", layout="wide")
st.title("Multi-Agent Research Pipeline")

with st.sidebar:
    st.header("Settings")
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Recent advances in RAG",
    )
    run_clicked = st.button(
        "Run Research",
        type="primary",
        use_container_width=True,
        disabled=not topic.strip(),
    )

if run_clicked:
    try:
        state = run_research_pipeline(topic.strip())
        st.success("Pipeline finished.")

        tab_report, tab_feedback, tab_search, tab_scraped = st.tabs(
            ["Final Report", "Critic Feedback", "Search Results", "Scraped Content"]
        )

        with tab_report:
            st.markdown(state["report"])

        with tab_feedback:
            st.markdown(state["feedback"])

        with tab_search:
            with st.expander("Raw search results", expanded=True):
                st.write(state["search_results"])

        with tab_scraped:
            with st.expander("Raw scraped content", expanded=True):
                st.write(state["scraped_content"])

    except Exception as e:
        st.error(f"Pipeline failed: {e}")
else:
    st.info("Enter a topic in the sidebar and click **Run Research** to start.")
