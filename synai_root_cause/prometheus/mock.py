import networkx as nx
import pandas as pd

from synai_root_cause.prometheus.client import PrometheusClient


class PrometheusMock(PrometheusClient):
    def __init__(self):
        self.examples_folder = "synai_root_cause/prometheus/response_examples"

    def get_callgraph(self) -> nx.DiGraph:
        df = pd.read_csv(self.examples_folder + "/callgraph.csv")
        graph = nx.DiGraph()
        for _, edge in df.iterrows():
            source = edge['source']
            destination = edge['destination']
            graph.add_edge(source, destination)

            graph.nodes()[source]['type'] = 'service'
            graph.nodes()[destination]['type'] = 'service'
        return graph

    def get_latency_df(self) -> pd.DataFrame:
        latency_df_source = pd.read_csv(self.examples_folder + "/latency_source_50.csv")
        latency_df_source = latency_df_source.set_index('timestamp').drop(columns=['Unnamed: 0'])
        latency_df_destination = pd.read_csv(self.examples_folder + "/latency_destination_50.csv")
        latency_df_destination = latency_df_destination.set_index('timestamp').drop(columns=['Unnamed: 0'])
        latency_df = latency_df_destination.add(latency_df_source)
        return latency_df

    def get_all_services_metrics_df(self) -> pd.DataFrame:
        columns = ["timestamp", "svc", "ctn_cpu", "ctn_memory", "ctn_network"]
        result_df = pd.DataFrame(columns=columns, index=["timestamp", "svc"])
        for svc_name in ['ratings-v1', 'ratings-v2', 'reviews-v2']:
            df = pd.read_csv(self.examples_folder + f"/test_metrics_{svc_name}.csv")
            df = df.set_index("timestamp").drop(columns=['Unnamed: 0'])
            df["svc"] = svc_name
            result_df = result_df.merge(df, how="outer", on=columns)
        return result_df
