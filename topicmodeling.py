import streamlit as st
import requests
import pandas as pd
from pyvis.network import Network
import streamlit.components.v1 as components
import time  # Importing the time module

def fetch_semantic_scholar_papers(topic, max_results=10, min_citations=0, start_year=None, end_year=None, retries=3):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": topic,
        "limit": max_results,
        "fields": "title,authors,year,citations"
    }

    papers = []
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
            time.sleep(1)

    if not papers:
        st.write("Failed to fetch data after multiple attempts.")

    return papers

def create_network_graph(papers):
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    for paper in papers:
        paper_id = paper.get('paperId')
        paper_title = ' '.join(paper.get('title', 'N/A')) if paper.get('title') else 'N/A'
        net.add_node(paper_id, label=paper_title, title=paper_title)

        for citation in paper.get('citations', []):
            cited_paper_id = citation.get('paperId')
            if cited_paper_id is None:
                continue

            net.add_node(cited_paper_id, label=cited_paper_id, title=cited_paper_id)
            net.add_edge(paper_id, cited_paper_id)

    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -80000,
          "centralGravity": 0.3,
          "springLength": 95
        },
        "minVelocity": 0.75
      }
    }
    """)

    return net

def main():
    st.title("Semantic Scholar Citation Network")
    topic = st.text_input("Enter a Topic", "Machine Learning", key="topic_input")
    max_results = st.slider("Max number of results", 5, 50, 10, key="max_results_slider")
    min_citations = st.slider("Minimum citations", 0, 100, 10, key="min_citations_slider")
    start_year = st.number_input("Start Year", min_value=1900, max_value=2023, value=2000, key="start_year_input")
    end_year = st.number_input("End Year", min_value=1900, max_value=2023, value=2023, key="end_year_input")
    run_button = st.button('Run Query', key="run_query_button")

    if run_button and topic:
        papers = fetch_semantic_scholar_papers(topic, max_results, min_citations, start_year, end_year)
        if papers:
            net = create_network_graph(papers)
            path = "temp_network.html"
            net.save_graph(path)
            HtmlFile = open(path, 'r', encoding='utf-8')
            source_code = HtmlFile.read()
            st.markdown(source_code, unsafe_allow_html=True)

            table_data = [{
                'Title': ' '.join(paper.get('title', ['N/A'])) if paper.get('title') else 'N/A',
                'Authors': ', '.join([author.get('name') for author in paper.get('authors', []) if 'name' in author]),
                'Year': paper.get('year', 'N/A'), 
                'Citations': len(paper.get('citations', []))
            } for paper in papers]

            df = pd.DataFrame(table_data)
            st.write(df)
        else:
            st.write("No papers found with the given criteria.")

if __name__ == "__main__":
    main()
