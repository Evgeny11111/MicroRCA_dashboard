from typing import List, Dict

from synai_root_cause.root_cause import RootCauseResults


def get_elements(results: RootCauseResults) -> List[Dict]:
    subgraph_nodes = results.get_subgraph_nodes()
    subgraph_edges = results.get_subgraph_edges_weight()
    subgraph_edges = results.get_subgraph_edges_weight()

    nodes = []
    for node in results.get_callgraph_nodes():
        item = {
            'data': {'id': node['label'], 'label': node['label']},
            'selectable': False
        }
        if node in subgraph_nodes:
            item['classes'] = 'subgraph-node'
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
                'line-color': '#3495eb'
            }
        },
        {
            'selector': '.subgraph-edge',
            'style': {
                'label': 'data(weight)',
                'text-rotation': 'autorotate',
                'text-background-color': 'white',
                'text-background-opacity': 1,
                'text-background-padding': '4px'

            }
        },
        {
            'selector': '.subgraph-node',
            'style': {
                'background-color': '#3495eb'
            }
        }
    ]
    return stylesheet
