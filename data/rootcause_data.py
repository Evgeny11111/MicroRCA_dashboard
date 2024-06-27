from typing import List, Dict

from synai_root_cause.root_cause import RootCauseResults


def get_elements(results: RootCauseResults) -> List[Dict]:
    top_root_causes = results.get_root_cause_nodes_top_n(2)
    root_cause_top_1, root_cause_top_2 = {}, {}
    if len(top_root_causes) == 1:
        root_cause_top_1 = results.get_root_cause_nodes_top_n(2)[0]
    if len(top_root_causes) >= 2:
        root_cause_top_1, root_cause_top_2 = results.get_root_cause_nodes_top_n(2)

    nodes = []
    for node in results.get_callgraph_nodes():
        item = {
            'data': {'id': node['label'], 'label': node['label']},
            'selectable': False
        }
        if node in [root_cause_top_1]:
            item['classes'] = 'root-cause-top-1'
        if node in [root_cause_top_2]:
            item['classes'] = 'root-cause-top-2'
        nodes.append(item)

    edges = []
    for edge in results.get_callgraph_edges():
        item = {
            'data': {'id': edge['source'] + '->' + edge['target'], 'source': edge['source'], 'target': edge['target']}
        }
        edges.append(item)

    elements = nodes
    elements.extend(edges)
    # print(elements)
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
                'curve-style': 'bezier',
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
            'selector': '.root-cause-top-1',
            'style': {
                'background-color': '#eb4934'
            }
        }
    ]
    return stylesheet
