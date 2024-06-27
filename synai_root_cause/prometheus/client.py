from abc import ABC, abstractmethod
import networkx as nx
import pandas as pd


class PrometheusClient(ABC):

    @abstractmethod
    def get_callgraph(self) -> nx.DiGraph:
        pass

    @abstractmethod
    def get_latency_df(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_all_services_metrics_df(self) -> pd.DataFrame:
        pass
