import streamlit as st
from scholarly import scholarly
import pandas as pd
import plotly.graph_objects as go
import time

def fetch_papers(topic, max_results=10, min_citations=0, start_year=None, end_year=None):
    search_query = scholarly.search_pubs(topic)
    papers = []

    while len(papers) < max_results:
        try:
            paper = next(search_query)
            year = int(paper.bib.get('year', 0))
            citedby = paper.bib.get('citedby', 0)

            if citedby >= min_citations and (start_year is None or year >= start_year) and (end_year is None or year <= end_year):
                papers.append(paper)
        except StopIteration:
            break
        except Exception:
            # You may choose to handle exceptions differently or not at all
            break

    return papers

def create_plotly_graph(papers):
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []
    node_text = []

    for i, paper in enumerate(papers):
        node_x.append(i)
        node_y.append(i)
        node_text.append(paper.bib['title'])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        marker=dict(size=10, line_width=2))

    fig = go.Figure(data=[node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                    )

    return fig

def main():
    st.title("Scholarly Topic Modeling")

    topic = st.text_input("Enter a Topic", "Machine Learning")
    max_results = st.slider("Max number of results", 5, 50, 10)
    min_citations = st.slider("Minimum citations", 0, 100, 10)
    start_year = st.number_input("Start Year", min_value=1900, max_value=2023, value=2000)
    end_year = st.number_input("End Year", min_value=1900, max_value=2023, value=2023)

    if topic:
        papers = fetch_papers(topic, max_results, min_citations, start_year, end_year)
        if papers:
            fig = create_plotly_graph(papers)
            st.plotly_chart(fig, use_container_width=True)

            data = [{'Title': paper.bib['title'], 'Authors': paper.bib.get('author', 'N/A'), 
                     'Year': paper.bib.get('year', 'N/A'), 'Citations': paper.bib.get('citedby', 0)} 
                    for paper in papers]
            df = pd.DataFrame(data)
            st.write(df)

if __name__ == "__main__":
    main()
