import time
from synai_root_cause.prometheus.api import PrometheusApi
from synai_root_cause.prometheus.client_impl import PrometheusClientImpl
from synai_root_cause.prometheus.mock import PrometheusMock
from synai_root_cause.root_cause import RootCauseAnalyzer


def root_cause_analyze(is_online, p_teleport, alpha, step, num_minutes_back):
    prometheus_url = 'http://prometheus-ci01994970-edevgen-synai-system.apps.dev-gen.sigma.sbrf.ru/api/v1/query_range'
    current_time = int(time.time())
    # current_time = 1642425000
    # num_minutes_back = 30  # количество минут назад - гиперпараметр
    delta_time = num_minutes_back * 60  # 30 минут умножаем на 60 секунд
    # step = 60  # сбор раз в минуту - гиперпараметр

    start_time = current_time - delta_time
    end_time = current_time

    if is_online:
        prom_client = PrometheusClientImpl(PrometheusApi(prometheus_url, start_time, end_time, step))
    else:
        prom_client = PrometheusMock()

    rca = RootCauseAnalyzer(prom_client)

    # alpha = 0.55  # вес аномального ребра - гиперпараметр
    # p_teleport = 0.50  # вероятность телепорта - гиперпараметр
    result = rca.get_root_cause(alpha=alpha, p_teleport=p_teleport)
    # print(result.anomaly_score)
    # print(result.get_root_cause_nodes_top_n(3))

    return result
