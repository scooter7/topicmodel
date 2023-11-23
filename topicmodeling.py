import streamlit as st
import requests
import plotly.graph_objects as go
import time

def fetch_semantic_scholar_papers(topic, max_results=10, min_citations=0, start_year=None, end_year=None, retries=3):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": max_results,
        "fields": "title,authors,year,citations"
    }

    papers = []  # Initialize the papers list
    attempt = 0

    while attempt < retries and not papers:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            for paper in response.json()['data']:
                year = int(paper.get('year', 0))
                citations = len(paper.get('citations', []))

                if citations >= min_citations and (start_year is None or year >= start_year) and (end_year is None or year <= end_year):
                    papers.append(paper)
                    if len(papers) >= max_results:
                        break
        else:
            st.write(f"Attempt {attempt + 1} failed with status code:", response.status_code)
            attempt += 1
            time.sleep(1)  # Wait for a second before retrying

    if not papers:
        st.write("Failed to fetch data after multiple attempts.")

    return papers

def create_network_graph(papers):
    fig = go.Figure()

    # Add nodes (papers)
    for paper in papers:
        title = paper.get('title', 'No Title')[0]  # Assuming title is a list
        authors = ', '.join([author.get('name') for author in paper.get('authors', []) if 'name' in author])
        node_label = f"{title} by {authors}"
        fig.add_trace(go.Scatter(x=[paper['paperId']], y=[0], mode='markers+text', text=node_label, name=paper['paperId']))

        # Add edges (citations)
        # This part needs to be adjusted based on how citations are structured in the Semantic Scholar data
        for citation in paper.get('citations', []):
            fig.add_trace(go.Scatter(x=[paper['paperId'], citation['paperId']], y=[0, 0], mode='lines'))

    # Set up graph layout
    fig.update_layout(
        title="Paper Citation Network",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )

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
