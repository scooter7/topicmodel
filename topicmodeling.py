import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

def fetch_crossref_articles(topic, max_results=10, min_citations=0, start_year=None, end_year=None):
    url = "https://api.crossref.org/works"
    params = {
        "query": topic,
        "rows": max_results,
        "sort": "is-referenced-by-count",
        "order": "desc"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        items = response.json()['message']['items']
        filtered_items = [item for item in items if item['is-referenced-by-count'] >= min_citations and 
                          'published-print' in item and 
                          start_year <= item['published-print']['date-parts'][0][0] <= end_year]
        return filtered_items
    else:
        return []

def create_plotly_graph(papers):
    edge_x = []
    edge_y = []
    node_x = []
    node_y = []
    node_text = []

    for i, paper in enumerate(papers):
        node_x.append(i)
        node_y.append(i)
        node_text.append(paper['title'][0] if 'title' in paper else 'No Title')

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
    run_button = st.button('Run Query')

    if run_button and topic:
        papers = fetch_crossref_articles(topic, max_results, min_citations, start_year, end_year)
        if papers:
            fig = create_plotly_graph(papers)
            st.plotly_chart(fig, use_container_width=True)

            data = [{'Title': paper.get('title', ['N/A'])[0], 
                     'Authors': ', '.join([author['name'] for author in paper.get('author', [])]), 
                     'Year': paper['published-print']['date-parts'][0][0] if 'published-print' in paper else 'N/A', 
                     'Citations': paper.get('is-referenced-by-count', 0)} 
                    for paper in papers]
            df = pd.DataFrame(data)
            st.write(df)
        else:
            st.write("No papers found with the given criteria.")

if __name__ == "__main__":
    main()
