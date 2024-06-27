from typing import List, Dict
import numpy as np

from synai_root_cause.root_cause import RootCauseResults


def get_elements(results: RootCauseResults) -> List[Dict]:
    subgraph_nodes = results.get_subgraph_nodes()
    subgraph_edges = results.get_subgraph_edges_weight()
    personalization = results.get_personalization()
    anomaly_nodes = results.get_anomaly_nodes()

    nodes = []
    for node in results.get_callgraph_nodes():
        item = {
            'data': {'id': node['label'], 'label': node['label']},
            'selectable': False
        }
        if node in subgraph_nodes:
            item['classes'] = 'subgraph-node'
            if node['label'] in anomaly_nodes:
                item['classes'] = item['classes'] + ' ' + 'anomaly-node'
                item['data']['weight'] = str(np.round(personalization[node['label']]*100, 1)) + '  \n' + item['data']['id']
            nodes.append(item)

    edges = []
    for edge in subgraph_edges:
        item = {
            'data': {'id': edge['source'] + '->' + edge['target'], 'source': edge['source'], 'target': edge['target'],
                     'weight': abs(edge['weight'])},
            'classes': 'subgraph-edge'
        }
        edges.append(item)

    elements = nodes
    elements.extend(edges)
    return elements


def get_stylesheet(results: RootCauseResults):
    stylesheet = [
        {
            'selector': 'node',
            'style': {
                'label': 'data(id)'
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
                'target-arrow-color': 'grey',
                'target-arrow-shape': 'triangle',
                'line-color': 'gray'
            }
        },
        {
            'selector': '.subgraph-edge',
            'style': {
                'target-arrow-color': '#3495eb',
                'target-arrow-shape': 'triangle',
                'line-color': '#3495eb',
                'opacity': 0.5
            }
        },
        {
            'selector': '.subgraph-node',
            'style': {
                'background-color': '#3495eb',
                'opacity': 0.5
            }
        },
        {
            'selector': '.anomaly-node',
            'style': {
                'background-color': '#3495eb',
                'label': 'data(weight)',
                'text-wrap': 'wrap',
                'opacity': 1
            }
        }
    ]
    return stylesheet
