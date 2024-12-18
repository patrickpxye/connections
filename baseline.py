import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from gensim.downloader import load
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances_argmin_min
from collections import defaultdict


def encode_words(word_list, model_type="glove"):
    if model_type == "glove":
        model = load("glove-wiki-gigaword-200")
    elif model_type == "word2vec":
        model = load("word2vec-google-news-300")
    else:
        raise ValueError("Unsupported model type. Use 'glove' or 'word2vec'.")

    word_embeddings = {}
    for word in word_list:
        try:
            word_embeddings[word] = model[word]
        except KeyError:
            word_embeddings[word] = None  # Word not in the vocabulary

    return word_embeddings


def balanced_kmeans(data, n_clusters, max_iter=100, tolerance=0.0001):
    kmeans = KMeans(n_clusters=n_clusters, max_iter=max_iter)
    labels = kmeans.fit_predict(data)
    centroids = kmeans.cluster_centers_

    for _ in range(max_iter):
        cluster_sizes = np.bincount(labels, minlength=n_clusters)
        target_size = len(data) // n_clusters

        while np.any(cluster_sizes != target_size):
            # Find the largest and smallest clusters
            overpopulated_clusters = np.where(cluster_sizes > target_size)[0]
            underpopulated_clusters = np.where(cluster_sizes < target_size)[0]

            if not len(overpopulated_clusters) or not len(underpopulated_clusters):
                break

            # Select a cluster pair to adjust
            for overpop_cluster in overpopulated_clusters:
                for underpop_cluster in underpopulated_clusters:
                    # Find points in the overpopulated cluster
                    points_in_overpop = np.where(labels == overpop_cluster)[0]
                    # Find the closest point to the centroid of the underpopulated cluster
                    point_to_move, _ = pairwise_distances_argmin_min(
                        data[points_in_overpop], centroids[[underpop_cluster]]
                    )
                    point_to_move = points_in_overpop[point_to_move[0]]

                    # Move the point
                    labels[point_to_move] = underpop_cluster
                    cluster_sizes = np.bincount(labels, minlength=n_clusters)

                    if (
                        cluster_sizes[overpop_cluster] <= target_size
                        or cluster_sizes[underpop_cluster] >= target_size
                    ):
                        break

        # Check for convergence (if no points were moved)
        new_centroids = np.array(
            [data[labels == i].mean(axis=0) for i in range(n_clusters)]
        )
        centroid_shift = np.linalg.norm(centroids - new_centroids, axis=1).sum()

        if centroid_shift < tolerance:
            break
        centroids = new_centroids

    return labels


def k_means_clustering(embeddings, n_clusters=4):
    # Filter out None values if there are missing embeddings
    filtered_embeddings = {
        word: emb for word, emb in embeddings.items() if emb is not None
    }

    # Prepare the data for clustering
    data = np.array(list(filtered_embeddings.values()))
    words = list(filtered_embeddings.keys())

    # Retrieve labels for each point
    labels = balanced_kmeans(data, n_clusters)

    # Create a dictionary to map each word to its cluster
    word_cluster = {words[i]: labels[i] for i in range(len(words))}

    return word_cluster


def visualize_clusters(embeddings, word_clusters, n_clusters=3):
    # Filter out None values and prepare data
    filtered_embeddings = [emb for emb in embeddings.values() if emb is not None]
    words = [word for word, emb in embeddings.items() if emb is not None]
    labels = [word_clusters[word] for word in words]

    # Reduce dimensions with PCA
    pca = PCA(n_components=2)  # Reduce to 2 dimensions for plotting
    reduced_data = pca.fit_transform(filtered_embeddings)

    # Create a scatter plot of the projected data
    plt.figure(figsize=(10, 8))
    colors = plt.cm.get_cmap("tab10", n_clusters)

    for i in range(len(reduced_data)):
        plt.scatter(
            reduced_data[i, 0],
            reduced_data[i, 1],
            color=colors(labels[i]),
            label=f"Cluster {labels[i]}",
        )

    # Add annotations to each point
    for i, word in enumerate(words):
        plt.annotate(
            word,
            (reduced_data[i, 0], reduced_data[i, 1]),
            textcoords="offset points",
            xytext=(0, 10),
            ha="center",
        )

    # Add legend and title
    plt.title("Word Embedding Clusters Visualization")
    plt.legend()
    plt.grid(True)
    plt.show()


# input should be json.load('data.json')
def transform_test_data(data, isLower):
    result = []
    for i, item in enumerate(data):
        entries = []
        solutions = []
        descriptions = []
        for answer in item["answers"]:
            entry = [word.lower() if isLower else word for word in answer["words"]]
            entries += entry
            solutions.append(entry)
            descriptions.append(answer["description"])
        result += [
            {"entries": entries, "solutions": solutions, "descriptions": descriptions}
        ]
    return result


def group_clusters(clusters):
    grouped_clusters = defaultdict(list)
    for k, v in clusters.items():
        print(k, v)
        grouped_clusters[v].append(k)
    return list(grouped_clusters.values())


def compute_iou(c1, c2):
    assert len(c1) != 0 and len(c2) != 0
    return len(set(c1) & set(c2)) / len(set(c1) | set(c2))


def evaluate_clusters_iou(pred_clusters, true_clusters):  # input as sets
    total_iou = []
    for pc in pred_clusters:
        ious = [compute_iou(pc, tc) for tc in true_clusters]
        total_iou.append(max(ious))
    return sum(total_iou) / len(total_iou)


# version of the earlier function that returns the list of ious, useful for difficulty analysis
def enumerate_clusters_iou(pred_clusters, true_clusters):
    total_iou = []
    for pc in pred_clusters:
        ious = [compute_iou(pc, tc) for tc in true_clusters]
        total_iou.append(max(ious))
    return total_iou


def evaluate_clusters_entropy(pred_clusters, true_clusters):
    total_entropy = 0
    for pc in pred_clusters:
        cluster_entropy = 0
        # formula: -sum(p*log(p))
        # p = probability of a data point being classified as true label in cluster pc.
        for tc in true_clusters:
            p = len(set(pc) & set(tc)) / len(pc)
            if p != 0:
                cluster_entropy += -p * np.log(p)
        total_entropy += cluster_entropy
    return total_entropy / len(pred_clusters)


def count_perfert_matches(pred_clusters, true_clusters):
    perfect_match = 0
    for pc in pred_clusters:
        if pc in true_clusters:
            perfect_match += 1
    return perfect_match
