import dash
from dash import dcc
import dash_cytoscape as cyto
import numpy as np
import pandas as pd
from dash import callback_context
from dash import dash_table
from dash import html
from dash.dependencies import Output, Input, State

from data import normal_graph_data, \
    anomaly_edges_data, \
    anomaly_subgraph_data, \
    anomaly_weighed_graph_data, \
    anomaly_scores_for_anomaly_nodes, \
    rootcause_data
from synai_root_cause.main import root_cause_analyze

app = dash.Dash(__name__, title="ROOTCAUSE DEMO")

# NAVBAR

online_btn = html.A('online', id='online-btn', n_clicks=0)
offline_btn = html.A('offline', id='offline-btn', n_clicks=0)
reset_btn = html.A('reset', id='reset-btn', n_clicks=0)

navbar = html.Ul(
    [
        html.Li(online_btn),
        html.Li(offline_btn),
        html.Li(reset_btn)
    ],
    id='navbar'
)

#PARAMS SLIDERS

# вероятность телепорта в аномальные ноды 0.15
param1 = dcc.Slider(
    id='param1-slider',
    min=0,
    max=1,
    step=0.05,
    value=0.15,
    tooltip={"placement": "bottom", "always_visible": True}

)

# alpha - вес аномального ребра 0.55
param2 = dcc.Slider(
    id='param2-slider',
    min=0,
    max=1,
    step=0.05,
    value=0.55,
    tooltip={"placement": "bottom", "always_visible": True}

)

# количество секунд между сбором данных 60
param3 = dcc.Slider(
    id='param3-slider',
    min=10,
    max=120,
    step=5,
    value=60,
    tooltip={"placement": "bottom", "always_visible": True}

)

# количество минут назад 30
param4 = dcc.Slider(
    id='param4-slider',
    min=10,
    max=120,
    step=10,
    value=30,
    tooltip={"placement": "bottom", "always_visible": True}

)
params = html.Div(
    [
        html.Div(
            [
                html.H4('Вероятность телепорта'),
                param1
            ],
            className='setting'
        ),
        html.Div(
            [
                html.H4('Вес аномального ребра'),
                param2
            ],
            className='setting'
        ),
        html.Div(
            [
                html.H4('Частота сбора данных в секундах для online'),
                param3
            ],
            className='setting'
        ),
        html.Div(
            [
                html.H4('Учитываемый временной промежуток в минутах для online'),
                param4
            ],
            className='setting'
        )
    ],
    id='params',
    style={'position': 'sticky', 'top': '0px', 'padding': '36px 0 0 0',  'z-index': '1', 'display': 'block-inline',
           'width': '45vw', 'margin-left': '90px', 'background-color': 'white'}
)

# NORAMAL GRAPH

normal_graph = cyto.Cytoscape(
    id='normal_graph',
    elements=[],
    stylesheet=[],
    panningEnabled=False,
    layout={
        'name': 'circle',
    },
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '50px 100px 50px 100px'}
)
n_clicks_off_prev = 0
n_clicks_on_prev = 0


@app.callback(
    Output('normal_graph', 'elements'),
    Output('normal_graph', 'stylesheet'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_normal_graph(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return [], []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        return normal_graph_data.get_elements(results), normal_graph_data.get_stylesheet(results)

    elif 'offline-btn' in changed_id:
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        return normal_graph_data.get_elements(results), normal_graph_data.get_stylesheet(results)
    return [], []


normal_graph_desc = html.Div(
    [
        html.H1('1. Построение графа вызовов'),
        html.P('Стрелка следует по направлению запроса')
    ],
    id="normal_graph_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '50px 100px 50px 100px'}
)

# ANOMALY EDGES

anomaly_edges = cyto.Cytoscape(
    id='anomaly_edges',
    elements=[],
    stylesheet=[],
    panningEnabled=False,
    layout={
        'name': 'circle',
    },
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)


@app.callback(
    Output('anomaly_edges', 'elements'),
    Output('anomaly_edges', 'stylesheet'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_anomaly_edges(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return [], []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        return anomaly_edges_data.get_elements(results), anomaly_edges_data.get_stylesheet(results)

    elif 'offline-btn' in changed_id:
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        return anomaly_edges_data.get_elements(results), anomaly_edges_data.get_stylesheet(results)

    return [], []


anomaly_edges_desc = html.Div(
    [
        html.H1('2. Выявление аномальных связей'),
        html.P('На графе вызовов выделены связи с аномальным response-time')
    ],
    id="anomaly_edges_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)

# ANOMALY SUBGRAPH

anomaly_subgraph = cyto.Cytoscape(
    id='anomaly_subgraph',
    elements=[],
    stylesheet=[],
    panningEnabled=False,
    layout={
        'name': 'circle',
    },
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)


@app.callback(
    Output('anomaly_subgraph', 'elements'),
    Output('anomaly_subgraph', 'stylesheet'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_anomaly_subgraph(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return [], []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        return anomaly_subgraph_data.get_elements(results), anomaly_subgraph_data.get_stylesheet(results)

    elif 'offline-btn' in changed_id:
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        return anomaly_subgraph_data.get_elements(results), anomaly_subgraph_data.get_stylesheet(results)

    return [], []


anomaly_subgraph_desc = html.Div(
    [
        html.H1('3. Выделение аномального подграфа'),
        html.P('Берутся аномальные ноды + смежные к ним')
    ],
    id="anomaly_subgraph_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)

# ANOMALY WEIGHTED GRAPH

anomaly_weighted_graph = cyto.Cytoscape(
    id='anomaly_weighted_graph',
    elements=[],
    stylesheet=[],
    panningEnabled=False,
    layout={
        'name': 'circle',
    },
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)


@app.callback(
    Output('anomaly_weighted_graph', 'elements'),
    Output('anomaly_weighted_graph', 'stylesheet'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_anomaly_weighted_graph(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return [], []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        return anomaly_weighed_graph_data.get_elements(results), anomaly_weighed_graph_data.get_stylesheet(results)

    elif 'offline-btn' in changed_id:
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        return anomaly_weighed_graph_data.get_elements(results), anomaly_weighed_graph_data.get_stylesheet(results)

    return [], []


anomaly_weighted_graph_desc = html.Div(
    [
        html.H1('4. Взвешивание граней подграфа'),
        html.P('Веса назначаются на основе корреляций метрик')
    ],
    id="anomaly_weighted_graph_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)

# ANOMALY SCORES FOR ANOMALY NODES

anomaly_nodes_scores = cyto.Cytoscape(
    id='anomaly_nodes',
    elements=[],
    stylesheet=[],
    panningEnabled=False,
    layout={
        'name': 'circle',
    },
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)


@app.callback(
    Output('anomaly_nodes', 'elements'),
    Output('anomaly_nodes', 'stylesheet'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_anomaly_nodes_scores(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return [], []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        return anomaly_scores_for_anomaly_nodes.get_elements(results), \
               anomaly_scores_for_anomaly_nodes.get_stylesheet(results)

    elif 'offline-btn' in changed_id:
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        return anomaly_scores_for_anomaly_nodes.get_elements(results), \
               anomaly_scores_for_anomaly_nodes.get_stylesheet(results)

    return [], []


anomaly_nodes_scores_desc = html.Div(
    [
        html.H1('5. Взвешивание аномальных вершин'),
        html.P('Для каждой аномальной вершины рассчитывается некоторый Anomaly Score, определяющий вероятность '
               'телепорта')
    ],
    id="anomaly_nodes_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)

# ROOTCAUSE GRAPH

rootcause_graph = cyto.Cytoscape(
    id='rootcause_graph',
    elements=[],
    stylesheet=[],
    panningEnabled=False,
    layout={
        'name': 'circle',
    },
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)


@app.callback(
    Output('rootcause_graph', 'elements'),
    Output('rootcause_graph', 'stylesheet'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_rootcause_graph(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return [], []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        return rootcause_data.get_elements(results), rootcause_data.get_stylesheet(results)
    elif 'offline-btn' in changed_id:
        # print('OFFLINE')
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        # print(f"Сравнение: {rootcause_data.get_elements(results)}")
        return rootcause_data.get_elements(results), rootcause_data.get_stylesheet(results)
    else:
        return [], []


rootcause_graph_desc = html.Div(
    [
        html.H1('6. Определение root cause'),
        html.P('Найденные причины ранжируются в соответствие с частотой визитов')
    ],
    id="rootcause_graph_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)

# ROOTCAUSE TABLE

rootcause_table = html.Div(
    '',
    id='rootcause_table',
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)


@app.callback(
    Output('rootcause_table', 'children'),
    Input('offline-btn', 'n_clicks'),
    Input('online-btn', 'n_clicks'),
    Input('reset-btn', 'n_clicks'),
    State('param1-slider', 'value'),
    State('param2-slider', 'value'),
    State('param3-slider', 'value'),
    State('param4-slider', 'value'),

)
def update_rootcause_graph(n_clicks_off, n_clicks_on, n_clicks_reset, p_teleport, alpha, step, num_minutes_back):
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if 'reset-btn' in changed_id:
        return []

    if 'online-btn' in changed_id:
        results = root_cause_analyze(True, p_teleport, alpha, step, num_minutes_back)
        data = results.anomaly_score
        if not data:
            return []
        df = pd.DataFrame(data)
        df.columns = ['name', 'value']
        df['value'] = np.round(df['value'] * 100, 1)
        table = dash_table.DataTable(
            id='table',
            columns=[{'name': 'Название сервиса', 'id': 'name'},
                     {'name': 'Вероятность, %', 'id': 'value'}],
            data=df.to_dict('records'),
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'fontFamily': '"PT Sans", sans-serif',
                'fontSize': '19px',
                'color': '#4287f5'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'value'},
                    'textAlign': 'right',
                    'fontFamily': "'PT Mono', monospace",
                    'fontSize': '15px',
                    'color': '#555659'
                },
                {
                    'if': {'column_id': 'name'},
                    'textAlign': 'left',
                    'fontFamily': '"PT Sans", sans-serif',
                    'fontSize': '15px',
                    'color': '#555659'
                }
            ],
            fill_width=False

        )
        return table

    elif 'offline-btn' in changed_id:
        results = root_cause_analyze(False, p_teleport, alpha, step, num_minutes_back)
        data = results.anomaly_score
        df = pd.DataFrame(data)
        df.columns = ['name', 'value']
        df['value'] = np.round(df['value'] * 100, 1)
        table = dash_table.DataTable(
            id='table',
            columns=[{'name': 'Название сервиса', 'id': 'name'},
                     {'name': 'Вероятность, %', 'id': 'value'}],
            data=df.to_dict('records'),
            style_header={
                'backgroundColor': 'white',
                'fontWeight': 'bold',
                'fontFamily': '"PT Sans", sans-serif',
                'fontSize': '19px',
                'color': '#4287f5'
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'value'},
                    'textAlign': 'right',
                    'fontFamily': "'PT Mono', monospace",
                    'fontSize': '15px',
                    'color': '#555659'
                },
                {
                    'if': {'column_id': 'name'},
                    'textAlign': 'left',
                    'fontFamily': '"PT Sans", sans-serif',
                    'fontSize': '15px',
                    'color': '#555659'
                }
            ],
            fill_width=False

        )
        return table

    else:
        return []


rootcause_table_desc = html.Div(
    [
        html.H1('7. Ранжированный список root cause'),
        html.P('По частоте посещений случайного блуждания сервисы ранжируются в порядке убывания частоты, '
               'самые верхние в этом списке сервисы являются наиболее вероятными причинами')
    ],
    id="rootcause_table_desc",
    className='desc',
    style={'width': '35vw', 'height': '35vh', 'background-color': 'white', 'box-shadow': '10px 10px 15px #999999',
           'padding': '40px', 'margin': '0px 100px 50px 100px'}
)

wrapper = html.Div(
    [
        normal_graph,
        normal_graph_desc,
        anomaly_edges,
        anomaly_edges_desc,
        anomaly_subgraph,
        anomaly_subgraph_desc,
        anomaly_weighted_graph,
        anomaly_weighted_graph_desc,
        anomaly_nodes_scores,
        anomaly_nodes_scores_desc,
        rootcause_graph,
        rootcause_graph_desc,
        rootcause_table,
        rootcause_table_desc
    ],
    className='container'
)

app.layout = html.Div(
    [
        navbar,
        params,
        wrapper
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True, port=9999)
