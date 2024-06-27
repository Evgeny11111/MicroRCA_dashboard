from typing import List, Dict

from synai_root_cause.root_cause import RootCauseResults


def get_elements(results: RootCauseResults) -> List[Dict]:
    anomaly_edges = results.get_anomal_rt_edges()
    nodes = [{
        'data': {'id': node['label'], 'label': node['label']},
        'selectable': False
    }
        for node in results.get_callgraph_nodes()]
    edges = []
    for edge in results.get_callgraph_edges():
        item = {
            'data': {'id': edge['source'] + '->' + edge['target'], 'source': edge['source'], 'target': edge['target']}
        }
        if edge in anomaly_edges:
            item['classes'] = 'anomaly'
        edges.append(item)

    elements = nodes
    elements.extend(edges)
    return elements


def get_stylesheet(results: RootCauseResults):
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'label': 'data(id)',
                'background-color': '#c2c2c2'
            },
        },
        {
            'selector': 'edge',
            'style': {
                'curve-style': 'bezier'
            }
        },
        {
            'selector': 'edge',
            'style': {
                'target-arrow-color': '#c2c2c2',
                'target-arrow-shape': 'triangle',
                'line-color': '#c2c2c2'
            }
        },
        {
            'selector': '.anomaly',
            'style': {
                'target-arrow-color': '#eb4934',
                'target-arrow-shape': 'triangle',
                'line-color': '#eb4934'
            }
        }
    ]
    return stylesheet
