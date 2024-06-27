from typing import List, Tuple, Dict
import networkx as nx
from synai_root_cause.prometheus.client import PrometheusClient
from synai_root_cause.anomaly_subgraph import anomaly_subgraph, birch_ad_with_smoothing


class RootCauseResults:
    def __init__(self, callgraph: nx.DiGraph, anomaly_edges: List[Tuple[str, str]], subgraph: nx.DiGraph, anomaly_score,
                 personalization: Dict[str, float]):
        self.callgraph = callgraph
        self.anomaly_edges = anomaly_edges
        self.subgraph = subgraph
        self.anomaly_score = anomaly_score
        self.personalization = personalization

    def get_callgraph_nodes(self):
        """
        :return: сервисы в формате
        [{'label': 'название сервиса 1'},
         {'label': 'название сервиса 2'}, ...]
        """
        result = []
        for node in self.callgraph.nodes:
            result.append({"label": node})
        return result

    def get_callgraph_edges(self):
        """
        :return: рёбра графа вызовов в формате
        [{'source': 'название сервиса 1', 'target': 'название сервиса 2'},
         {.....}]
        """
        result = []
        for edge in self.callgraph.edges:
            result.append({"source": edge[0], "target": edge[1]})
        return result

    def get_anomal_rt_edges(self):
        """
        :return: аномальные рёбра графа в формате
        [{'source': 'название сервиса 1', 'target': 'название сервиса 2'},
         {.....}]
        """
        result = []
        for edge in self.anomaly_edges:
            result.append({"source": edge[0], "target": edge[1]})
        return result

    def get_subgraph_nodes(self):
        """
        :return: сервисы в формате
        [{'label': 'название сервиса 1'},
         {'label': 'название сервиса 2'}, ...]
        """
        result = []
        for node in self.subgraph.nodes:
            result.append({"label": node})
        return result

    def get_subgraph_edges(self):
        """
        :return: аномальные рёбра графа в формате
        [{'source': 'название сервиса 1', 'target': 'название сервиса 2'},
         {.....}]
        """
        result = []
        for edge in self.subgraph.edges():
            result.append({"source": edge[1], "target": edge[0]})
        return result

    def get_subgraph_edges_weight(self):
        """
        :return: аномальные рёбра графа в формате
        [{'source': 'название сервиса 1', 'target': 'название сервиса 2', 'weight': '0.55'},
         {.....}]
        """
        result = []
        for edge in self.subgraph.edges(data=True):
            result.append({"source": edge[0], "target": edge[1], "weight": edge[2]["weight"]})
        return result

    def get_personalization(self):
        """
        :return: anomaly scores для аномальных вершин графа в формате
        {'название сервиса 1': 0.55, 'название сервиса 2': 0.17, .....}
        """
        return self.personalization

    def get_anomaly_nodes(self):
        """
        :return: список аномальных вершин
        ['название сервиса 1', 'название сервиса 2', .....]
        """
        result = []
        for edge in self.anomaly_edges:
            result.append(edge[1])
        return result

    def get_root_cause_nodes_top_n(self, n):
        """
        :return: сервисы в формате
        [{'label': 'название сервиса 1'},
         {'label': 'название сервиса 2'}, ...]
        """
        result = []
        i = 0
        for node, score in self.anomaly_score:
            # if node != 'productpage-v1':
                result.append({"label": node})
                i += 1
                if i >= n:
                    break
        return result


class RootCauseAnalyzer:
    def __init__(self, prom_client: PrometheusClient):
        self.prom_client = prom_client

    def get_root_cause(self, alpha, p_teleport) -> RootCauseResults:
        latency_df = self.prom_client.get_latency_df()
        ad_threshold = 0.045
        smoothing_window = 12
        anomalies = birch_ad_with_smoothing(latency_df, ad_threshold, smoothing_window)
        anomaly_edges = [tuple(edge.split("_")) for edge in anomalies]
        # print(f"anomalies = {anomalies}")
        callgraph = self.prom_client.get_callgraph()
        # alpha = 0.55  # вес аномального ребра
        # Get all metrics by all services
        metrics_df = self.prom_client.get_all_services_metrics_df()

        metrics_df.dropna(inplace=True)
        metrics_df.sort_values(by=['timestamp'], inplace=True)

        anomaly_graph, anomaly_score, personalization = anomaly_subgraph(metrics_df, callgraph, anomalies, latency_df, alpha, p_teleport)
        return RootCauseResults(callgraph=callgraph, anomaly_edges=anomaly_edges,
                                subgraph=anomaly_graph, anomaly_score=anomaly_score, personalization=personalization)
