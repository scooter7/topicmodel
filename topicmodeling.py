import streamlit as st
import requests
import plotly.graph_objects as go

def fetch_semantic_scholar_papers(topic, max_results=10, min_citations=0, start_year=None, end_year=None, retries=3):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": max_results,
        "fields": "title,authors,year,citations"
    }

    attempt = 0
    while attempt < retries:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # Process and filter papers here
            return papers
        else:
            st.write(f"Attempt {attempt + 1} failed with status code:", response.status_code)
            attempt += 1
            time.sleep(1)  # Wait for a second before retrying

    st.write("Failed to fetch data after multiple attempts.")
    return []

def create_network_graph(papers):
    fig = go.Figure()

    for paper in papers:
        paper_id = paper['paperId']
        fig.add_trace(go.Scatter(x=[paper_id], y=[0], mode='markers+text', text=paper['title'], name=paper_id))

        for citation in paper.get('citations', []):
            cited_paper_id = citation['paperId']
            fig.add_trace(go.Scatter(x=[paper_id, cited_paper_id], y=[0, 0], mode='lines', name=f"Citation: {cited_paper_id}"))

    return fig

def main():
    st.title("Semantic Scholar Citation Network")
    topic = st.text_input("Enter a Topic", "Machine Learning")
    max_results = st.slider("Max number of results", 5, 50, 10)
    min_citations = st.slider("Minimum citations", 0, 100, 10)
    start_year = st.number_input("Start Year", min_value=1900, max_value=2023, value=2000)
    end_year = st.number_input("End Year", min_value=1900, max_value=2023, value=2023)
    run_button = st.button('Run Query')

    if run_button and topic:
        papers = fetch_semantic_scholar_papers(topic, max_results, min_citations, start_year, end_year)
        if papers:
            fig = create_network_graph(papers)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No papers found with the given criteria.")

if __name__ == "__main__":
    main()
