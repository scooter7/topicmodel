import streamlit as st
import requests
import plotly.graph_objects as go

def fetch_semantic_scholar_papers(topic, max_results=10):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": max_results,
        "fields": "title,authors,year,citations"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['data']
    else:
        st.write("Failed to fetch data:", response.status_code)
        return []

def create_network_graph(papers):
    fig = go.Figure()

    # Add nodes and edges (citations)
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
    run_button = st.button('Run Query')

    if run_button and topic:
        papers = fetch_semantic_scholar_papers(topic)
        if papers:
            fig = create_network_graph(papers)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No papers found with the given criteria.")

if __name__ == "__main__":
    main()
