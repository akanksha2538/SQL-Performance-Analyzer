import matplotlib.pyplot as plt
import os


GRAPH_FOLDER = "static/graphs"

os.makedirs(GRAPH_FOLDER, exist_ok=True)


# -----------------------------------------
# Execution Time Graph
# -----------------------------------------

def create_execution_graph(query_times):

    graph_path = os.path.join(
        GRAPH_FOLDER,
        "execution_time.png"
    )

    labels = list(query_times.keys())
    values = list(query_times.values())

    plt.figure(figsize=(8, 4))

    plt.bar(labels, values)

    plt.xlabel("Queries")
    plt.ylabel("Execution Time (Seconds)")
    plt.title("SQL Query Execution Time")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(graph_path)

    plt.close()

    return graph_path


# -----------------------------------------
# Fastest vs Slowest Graph
# -----------------------------------------

def create_fastest_slowest_graph(fastest, slowest):

    graph_path = os.path.join(
        GRAPH_FOLDER,
        "fastest_slowest.png"
    )

    labels = ["Fastest", "Slowest"]
    values = [fastest, slowest]

    plt.figure(figsize=(5,4))

    plt.bar(labels, values)

    plt.ylabel("Execution Time (Seconds)")
    plt.title("Fastest vs Slowest Query")

    plt.tight_layout()

    plt.savefig(graph_path)

    plt.close()

    return graph_path


# -----------------------------------------
# Query Statistics Pie Chart
# -----------------------------------------

def create_statistics_pie(total_queries, slow_queries):

    graph_path = os.path.join(
        GRAPH_FOLDER,
        "query_statistics.png"
    )

    fast_queries = total_queries - slow_queries

    labels = [
        "Fast Queries",
        "Slow Queries"
    ]

    values = [
        fast_queries,
        slow_queries
    ]

    plt.figure(figsize=(5,5))

    plt.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Query Statistics")

    plt.savefig(graph_path)

    plt.close()

    return graph_path