import matplotlib.pyplot as plt
import os


def create_comparison_graph(before_time, after_time):

    labels = ["Before", "After"]
    values = [before_time, after_time]

    plt.figure(figsize=(5, 4))
    plt.bar(labels, values)

    plt.title("Query Performance Comparison")
    plt.ylabel("Execution Time (Seconds)")

    graph_folder = "static/graphs"

    os.makedirs(graph_folder, exist_ok=True)

    graph_path = os.path.join(
        graph_folder,
        "comparison.png"
    )

    plt.savefig(graph_path)
    plt.close()

    return graph_path