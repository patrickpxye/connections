import numpy as np

def compute_iou(c1, c2):
    assert len(c1) != 0 and len(c2) != 0
    return len(set(c1) & set(c2)) / len(set(c1) | set(c2))


def evaluate_clusters_iou(pred_clusters, true_clusters):  # input as sets
    total_iou = []
    for pc in pred_clusters:
        ious = [compute_iou(pc, tc) for tc in true_clusters]
        total_iou.append(max(ious))
    return sum(total_iou) / len(total_iou)

def evaluate_clusters_entropy(pred_clusters, true_clusters):
    total_entropy = 0
    for pc in pred_clusters:
        cluster_entropy = 0
        #formula: -sum(p*log(p))
        #p = probability of a data point being classified as true label in cluster pc.
        for tc in true_clusters:
            p = len(set(pc) & set(tc)) / len(pc)
            if p != 0:
                cluster_entropy += -p * np.log(p)
        total_entropy += cluster_entropy
    return total_entropy / len(pred_clusters)

def count_matches(pred_clusters, true_clusters):
    perfect_match  = np.zeros(len(true_clusters))
    for i, tc in enumerate(true_clusters):
        for pc in pred_clusters:
            if set(pc) == set(tc):
                perfect_match[i] = 1
    return perfect_match