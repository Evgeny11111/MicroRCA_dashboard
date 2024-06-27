from typing import Dict, Any
import requests

from synai_root_cause.prometheus.metric_names import *


class PrometheusApi:
    def __init__(self, api_url: str, start_time: int, end_time: int, step: int):
        self.api_url = api_url
        self.start_time = start_time
        self.end_time = end_time
        self.step = step

    def get_istio_requests_total(self) -> Dict[str, Any]:
        query = "sum by (source_workload,destination_workload) (istio_requests_total{destination_workload!='istio-telemetry'})"
        return self.prometheus_request_(query)

    def get_rt_latency_source(self) -> Dict[str, Any]:
        query = "histogram_quantile(0.90, sum(irate(istio_request_duration_seconds_bucket{reporter='source'}[10m])) by (destination_workload, source_workload, le))"
        return self.prometheus_request_(query)

    def get_rt_latency_destination(self) -> Dict[str, Any]:
        query = "histogram_quantile(0.90, sum(irate(istio_request_duration_seconds_bucket{reporter='destination'}[10m])) by (destination_workload, source_workload, le))"
        return self.prometheus_request_(query)

    def get_rate_metrics(self, metric_name: str) -> Dict[str, Any]:
        if metric_name not in [
                cpu_metric_name,
                memory_metric_name,
                network_metric_name]:
            raise ValueError("don't know such metric")
        agg = """{container!='istio-proxy', container=~'.+'}"""
        query = f"""sum by (container,pod,namespace,deployment) (({metric_name}{agg} - {metric_name}{agg} offset 1m))>=0"""
        return self.prometheus_request_(query)

    def get_raw_metrics(self, metric_name: str) -> Dict[str, Any]:
        if metric_name not in [
                cpu_metric_name,
                memory_metric_name,
                network_metric_name]:
            raise ValueError("don't know such metric")
        agg = """{container!='istio-proxy', container=~'.+'}"""
        query = f"""sum by (container,pod,namespace,deployment) ({metric_name}{agg})"""
        return self.prometheus_request_(query)

    def prometheus_request_(self, query: str) -> Dict[str, Any]:
        response = requests.get(self.api_url,
                                params={
                                    "query": query,
                                    "start": self.start_time,
                                    "end": self.end_time,
                                    "step": self.step})
        return response.json()
