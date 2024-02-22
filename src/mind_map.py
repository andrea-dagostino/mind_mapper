import networkx as nx
from graphviz import Digraph

import plotly.express as px
import plotly.graph_objects as go


def create_plotly_mind_map(data: dict) -> go.Figure:
    """
    data is a dictionary containing the following
    { "relationships": [{"source": ..., "target": ..., "type": ...}, {...}] }
    source: The source node
    target: The target node
    type: The type of the relationship between the source and target nodes
    """
    ### START - NETWORKX LOGIC ###
    # Create a directed graph
    G = nx.DiGraph()

    # Add edges to the graph
    for relationship in data["relationships"]:
        G.add_edge(
            relationship["source"], relationship["target"], type=relationship["type"]
        )

    # Create a layout for our nodes
    layout = nx.spring_layout(G, seed=42)

    traces = []
    for relationship in data["relationships"]:
        x0, y0 = layout[relationship["source"]]
        x1, y1 = layout[relationship["target"]]
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            line=dict(width=0.5, color="#888"),  # Set a single color for all edges
            hoverinfo="none",
            mode="lines",
        )
        traces.append(edge_trace)

    # Modify node trace to color based on source node
    node_x = []
    node_y = []
    for node in G.nodes():
        x, y = layout[node]
        node_x.append(x)
        node_y.append(y)

    ### END - NETWORKX LOGIC ###

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        # add text to the nodes and origin
        text=[node for node in G.nodes()],
        hoverinfo="text",
        marker=dict(
            showscale=False,
            colorscale="Greys",  # Change colorscale to grayscale
            reversescale=True,
            size=20,
            color='#505050',  # Set node color to gray
            line_width=2,
        ),
    )

    # Add node and edge labels
    edge_annotations = []
    for edge in G.edges(data=True):
        x0, y0 = layout[edge[0]]
        x1, y1 = layout[edge[1]]
        edge_annotations.append(
            dict(
                x=(x0 + x1) / 2,
                y=(y0 + y1) / 2,
                xref="x",
                yref="y",
                text=edge[2]["type"],
                showarrow=False,
                font=dict(size=10),
            )
        )

    node_annotations = []
    for node in G.nodes():
        x, y = layout[node]
        node_annotations.append(
            dict(
                x=x,
                y=y,
                xref="x",
                yref="y",
                text=node,
                showarrow=False,
                font=dict(size=12),
            )
        )

    # node_trace.marker.color = [len(G.edges(node)) for node in G.nodes()]
    node_trace.text = [node for node in G.nodes()]

    # Create the figure
    fig = go.Figure(
        data=traces + [node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode="closest",
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=edge_annotations,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        ),
    )

    # Modify the layout to include the legend
    fig.update_layout(
        legend=dict(
            title="Origins",
            traceorder="normal",
            font=dict(size=12),
        )
    )

    # Modify the node text color for better visibility on dark background
    node_trace.textfont = dict(color="white")

    # Modify the layout to include the legend and set the plot background to dark
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,1)",  # Set the background color to black
        plot_bgcolor="rgba(0,0,0,1)",  # Set the plot area background color to black
        legend=dict(
            title="Origins",
            traceorder="normal",
            font=dict(size=12, color="white"),  # Set legend text color to white
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    # Update the color of the edge annotations for better visibility
    for annotation in edge_annotations:
        annotation["font"]["color"] = "white"  # Set edge annotation text color to white

    # Update the color of the node annotations for better visibility
    for annotation in node_annotations:
        annotation["font"]["color"] = "white"  # Set node annotation text color to white

    # Update the edge trace color to be more visible on a dark background
    for trace in traces:
        if "line" in trace:
            trace["line"][
                "color"
            ] = "#888"  # Set edge color to a single color for all edges

    # Update the node trace marker border color for better visibility
    node_trace.marker.line.color = "white"

    return fig
