import pandas as pd
import networkx as nx
import numpy as np
from sklearn.cluster import Birch
from sklearn import preprocessing


# Anomaly Detection
def birch_ad_with_smoothing(latency_df, threshold, smoothing_window):
    # anomaly detection on response time of service invocation.
    # input: response times of service invocations, threshold for birch clustering
    # output: anomalous service invocation

    anomalies = []
    for svc, latency in latency_df.iteritems():
        # No anomaly detection in db
        if svc != 'timestamp' and 'Unnamed' not in svc and 'rabbitmq' not in svc and 'db' not in svc:
            latency = latency.rolling(window=smoothing_window, min_periods=1).mean()
            x = np.array(latency)
            x = np.where(np.isnan(x), 0, x)
            normalized_x = preprocessing.normalize([x])

            X = normalized_x.reshape(-1, 1)

            #            threshold = 0.05

            brc = Birch(branching_factor=50, n_clusters=None, threshold=threshold, compute_labels=True)
            brc.fit(X)
            brc.predict(X)

            labels = brc.labels_
            #            centroids = brc.subcluster_centers_
            n_clusters = np.unique(labels).size
            if n_clusters > 1:
                anomalies.append(svc)
    return anomalies


def get_service_metrics(metrics_df: pd.DataFrame, service_name: str) -> pd.DataFrame:
    return metrics_df[metrics_df['svc'] == service_name]


def node_weight(metrics_df: pd.DataFrame, svc, anomaly_graph, baseline_df):
    # print(f"node_weight for {svc}")

    # Get the average weight of the in_edges
    in_edges_weight_avg = 0.0
    num = 0
    for u, v, data in anomaly_graph.in_edges(svc, data=True):
        num = num + 1
        in_edges_weight_avg = in_edges_weight_avg + data['weight']
    if num > 0:
        in_edges_weight_avg  = in_edges_weight_avg / num

    df = get_service_metrics(metrics_df, svc)
    node_cols = ['node_cpu', 'node_network', 'node_memory']
    max_corr = 0.01
    metric = 'node_cpu'
    for col in node_cols:
        temp = abs(np.corrcoef(baseline_df[svc].values, df[col].values)[0, 1])
        if temp > max_corr:
            max_corr = temp
            metric = col
    data = in_edges_weight_avg * max_corr
    return data, metric


def svc_personalization(metrics_df: pd.DataFrame, svc, anomaly_graph, baseline_df):
    # print(f"svc_personalization for {svc}")

    df = get_service_metrics(metrics_df, svc)
    ctn_cols = ['ctn_cpu', 'ctn_network', 'ctn_memory']
    max_corr = 0.01
    metric = 'ctn_cpu'
    for col in ctn_cols:
        if len(baseline_df[svc].values) > len(df[col].values):
            baseline_df = baseline_df.loc[df.timestamp.unique(), :]
        temp = abs(np.corrcoef(baseline_df[svc].values, df[col].values)[0, 1])
        if temp > max_corr:
            max_corr = temp
            metric = col


    edges_weight_avg = 0.0
    num = 0
    for u, v, data in anomaly_graph.in_edges(svc, data=True):
        num = num + 1
        edges_weight_avg = edges_weight_avg + data['weight']

    for u, v, data in anomaly_graph.out_edges(svc, data=True):
        if anomaly_graph.nodes[v]['type'] == 'service':
            num = num + 1
            edges_weight_avg = edges_weight_avg + data['weight']

    edges_weight_avg  = edges_weight_avg / num

    personalization = edges_weight_avg * max_corr

    return personalization, metric


def anomaly_subgraph(metrics_df: pd.DataFrame, DG, anomalies, latency_df, alpha, p_teleport):
    # Get the anomalous subgraph and rank the anomalous services
    # input:
    #   DG: attributed graph
    #   anomlies: anoamlous service invocations
    #   latency_df: service invocations from data collection
    #   agg_latency_dff: aggregated service invocation
    #   faults_name: prefix of csv file
    #   alpha: weight of the anomalous edge
    # output:
    #   anomalous scores

    # Get reported anomalous nodes

    edges = []
    nodes = []

    baseline_df = pd.DataFrame()
    edge_df = {}
    for anomaly in anomalies:
        edge = anomaly.split('_')
        edges.append(tuple(edge))
        svc = edge[1]
        nodes.append(svc)
        baseline_df[svc] = latency_df[anomaly]
        edge_df[svc] = anomaly

    baseline_df.fillna(method='ffill', inplace=True)
    latency_df.fillna(method='ffill', inplace=True)

    nodes = set(nodes)

    personalization = {}
    for node in DG.nodes():
        if node in nodes:
            personalization[node] = 0

    # Get the subgraph of anomaly
    anomaly_graph = nx.DiGraph()
    for node in nodes:
        for u, v, data in DG.in_edges(node, data=True):
            edge = (u, v)
            if edge in edges:
                data = alpha
            else:
                normal_edge = u + '_' + v
                data = np.corrcoef(baseline_df[v].values, latency_df[normal_edge].values)[0, 1]

            data = round(data, 3)
            anomaly_graph.add_edge(u, v, weight=data)
            anomaly_graph.nodes[u]['type'] = DG.nodes[u]['type']
            anomaly_graph.nodes[v]['type'] = DG.nodes[v]['type']

        # Set personalization with container resource usage
        for u, v, data in DG.out_edges(node, data=True):
            edge = (u, v)
            if edge in edges:
                data = alpha
            else:

                if DG.nodes[v]['type'] == 'host':
                    data, col = node_weight(metrics_df, u, anomaly_graph, baseline_df)
                else:
                    normal_edge = u + '_' + v
                    data = np.corrcoef(baseline_df[u].values, latency_df[normal_edge].values)[0, 1]
            data = round(data, 3)
            anomaly_graph.add_edge(u, v, weight=data)
            anomaly_graph.nodes[u]['type'] = DG.nodes[u]['type']
            anomaly_graph.nodes[v]['type'] = DG.nodes[v]['type']

    for node in nodes:
        max_corr, col = svc_personalization(metrics_df, node, anomaly_graph, baseline_df)
        personalization[node] = max_corr / anomaly_graph.degree(node)

    anomaly_graph = anomaly_graph.reverse(copy=True)

    edges = list(anomaly_graph.edges(data=True))
    # print(f"anomaly edges = {edges}")

    # p_teleport = 0.50
    anomaly_score = nx.pagerank(anomaly_graph, alpha=1-p_teleport, personalization=personalization, max_iter=10000)

    anomaly_score = sorted(anomaly_score.items(), key=lambda x: x[1], reverse=True)

    # print(personalization)

    #    return anomaly_graph
    return anomaly_graph, anomaly_score, personalization
