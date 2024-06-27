import networkx as nx
import pandas as pd

from synai_root_cause.prometheus.client import PrometheusClient
from synai_root_cause.prometheus.api import PrometheusApi

from synai_root_cause.prometheus.metric_names import *


class PrometheusClientImpl(PrometheusClient):
    def __init__(self, prom_api: PrometheusApi):
        self.prom_api = prom_api

    def get_callgraph(self) -> nx.DiGraph:
        graph = nx.DiGraph()
        df = pd.DataFrame(columns=['source', 'destination'])
        response = self.prom_api.get_istio_requests_total()
        results = response["data"]["result"]

        for result in results:
            metric = result['metric']

            source = metric['source_workload']
            destination = metric['destination_workload']
            df = df.append({'source': source, 'destination': destination}, ignore_index=True)
            graph.add_edge(source, destination)

            graph.nodes()[source]['type'] = 'service'
            graph.nodes()[destination]['type'] = 'service'
        return graph

    def get_latency_df(self) -> pd.DataFrame:
        latency_df_source = self.get_latency_source_50_()
        latency_df_destination = self.get_latency_destination_50_()
        latency_df = latency_df_destination.add(latency_df_source)
        return latency_df

    def get_all_services_metrics_df(self) -> pd.DataFrame:
        cpu_df = self.get_all_services_metric(cpu_metric_name, 'rate')
        memory_df = self.get_all_services_metric(memory_metric_name)
        network_df = self.get_all_services_metric(network_metric_name)
        metrics_df = cpu_df.merge(memory_df, how='outer', on=['namespace', 'pod', 'container', 'svc', 'timestamp'])
        metrics_df = metrics_df.merge(network_df, how='outer', on=['namespace', 'pod', 'container', 'svc', 'timestamp'])
        metrics_df = metrics_df.rename(columns={cpu_metric_name: "ctn_cpu",
                                                memory_metric_name: "ctn_memory",
                                                network_metric_name: "ctn_network"})
        metrics_df = metrics_df[['timestamp', 'svc', 'ctn_cpu', 'ctn_memory', 'ctn_network']]
        return metrics_df

    def get_latency_source_50_(self) -> pd.DataFrame:
        latency_df = pd.DataFrame()
        response = self.prom_api.get_rt_latency_source()
        results = response['data']['result']

        for result in results:
            dest_svc = result['metric']['destination_workload']
            src_svc = result['metric']['source_workload']
            name = src_svc + '_' + dest_svc
            values = result['values']

            values = list(zip(*values))
            if 'timestamp' not in latency_df:
                timestamp = values[0]
                latency_df['timestamp'] = timestamp
                latency_df['timestamp'] = latency_df['timestamp'].astype('datetime64[s]')
            metric = values[1]
            latency_df[name] = pd.Series(metric)
            latency_df[name] = latency_df[name].astype('float64') * 1000

        latency_df = latency_df.set_index('timestamp')
        return latency_df

    def get_latency_destination_50_(self) -> pd.DataFrame:
        latency_df = pd.DataFrame()
        response = self.prom_api.get_rt_latency_destination()
        results = response['data']['result']

        for result in results:
            dest_svc = result['metric']['destination_workload']
            src_svc = result['metric']['source_workload']
            name = src_svc + '_' + dest_svc
            values = result['values']

            values = list(zip(*values))
            if 'timestamp' not in latency_df:
                timestamp = values[0]
                latency_df['timestamp'] = timestamp
                latency_df['timestamp'] = latency_df['timestamp'].astype('datetime64[s]')
            metric = values[1]
            latency_df[name] = pd.Series(metric)
            latency_df[name] = latency_df[name].astype('float64') * 1000

        latency_df = latency_df.set_index('timestamp')
        return latency_df

    def get_all_services_metric(self, metric_name: str, agg: str = 'raw') -> pd.DataFrame:
        response = self.prom_api.get_raw_metrics(metric_name)
        if agg == 'rate':
            response = self.prom_api.get_rate_metrics(metric_name)
        elif agg == 'raw':
            response = self.prom_api.get_raw_metrics(metric_name)
        results = response['data']['result']
        result_metrics = []
        for result in results:
            result_metrics.extend({'namespace': result['metric']['namespace'],
                                   'pod': result['metric']['pod'],
                                   'container': result['metric'].get('container'),
                                   'svc': pod_name_to_service_name(result['metric']['pod']),
                                   'timestamp': time_val[0],
                                   metric_name: float(time_val[1])
                                   } for time_val in result['values'])
        metric_df = pd.DataFrame(result_metrics)
        metric_df['timestamp'] = metric_df['timestamp'].astype('datetime64[s]')
        metric_df = metric_df[metric_df["container"] != "POD"]
        metric_df = metric_df[metric_df["namespace"] == "ci01994970-edevgen-synai-dev"]
        return metric_df


def pod_name_to_service_name(pod_name):
    pieces = pod_name.split("-")
    return "-".join(pieces[:-2])
