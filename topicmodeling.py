import streamlit as st
from scholarly import scholarly
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import time
import logging

def fetch_papers(topic, max_results=10, retry_limit=3, retry_delay=5):
    search_query = scholarly.search_pubs(topic)
    papers = []
    retry_count = 0

    while len(papers) < max_results and retry_count < retry_limit:
        try:
            paper = next(search_query).fill()
            papers.append(paper.__dict__)
        except StopIteration:
            break
        except Exception as e:
            logging.warning(f"An error occurred: {e}")
            retry_count += 1
            time.sleep(retry_delay)

    if retry_count == retry_limit:
        logging.warning("Reached maximum retry limit. Some papers may not be fetched.")
    return papers

def create_graph(papers):
    G = nx.Graph()
    for paper in papers:
        # Check if 'title' and 'author' are in the paper dictionary
        if 'title' in paper and 'author' in paper:
            paper_title = paper['title']
            G.add_node(paper_title, title=paper_title, size=paper.get('citedby', 10))
            authors = paper['author'].split(' and ')
            for author in authors:
                G.add_node(author, title=author, size=20)
                G.add_edge(paper_title, author)
    return G

def show_graph(G):
    net = Network(height='500px', width='100%', bgcolor='#222222', font_color='white', notebook=True)
    net.from_nx(G)
    net.show('graph.html')

    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
    net.save_graph(tmp_file.name)
    return tmp_file.name

def main():
    st.title("Scholarly Topic Modeling")

    topic = st.text_input("Enter a Topic", "Machine Learning")
    max_results = st.slider("Max number of results", 5, 50, 10)

    if topic:
        papers = fetch_papers(topic, max_results)
        if papers:
            G = create_graph(papers)
            graph_html_file = show_graph(G)
            st.components.v1.html(open(graph_html_file, 'r', encoding='utf-8').read(), height=600)

            data = [{'Title': paper.bib['title'], 'Authors': paper.bib.get('author', 'N/A'), 
                     'Year': paper.bib.get('year', 'N/A'), 'Citations': paper.bib.get('citedby', 0)} 
                    for paper in papers]
            df = pd.DataFrame(data)
            st.write(df)

if __name__ == "__main__":
    main()
