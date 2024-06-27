elements = [
    {
        'data': {'id': 'A', 'label': 'A'},
        'selectable': False,
        "classes" : 'rootcause',
    },
    {
        'data': {'id': 'B', 'label': 'B'},
        'selectable': False,

    },
    {
        'data': {'id': 'C', 'label': 'C'},
        'selectable': False
    },
    {
        'data': {'id': 'D', 'label': 'D'},
        'selectable': False
    },
    {
        'data': {'id': 'E', 'label': 'E'},
        'selectable': False
    },
    {
        'data': {'id': 'AB', 'source': 'A', 'target': 'B'},
        'classes': 'anomaly'

    },
    {
        'data': {'id': 'BC', 'source': 'B', 'target': 'C'},
        'classes': 'anomaly'

    },
    {
        'data': {'id': 'BD', 'source': 'B', 'target': 'D'},

    },
    {
        'data': {'id': 'AE', 'source': 'A', 'target': 'E'}
    },
]

stylesheet = [
    {
        'selector': 'node', 
        'style': {
            'label': 'data(id)'
        }, 
    },
    {
        'selector': '.rootcause',
        'style': {
            'background-color': '#ff6f5c'
        }
    },
    {
            'selector': 'edge',
            'style': {
                # The default curve style does not work with certain arrows
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
            'selector': '.anomaly',
            'style': {
                    'target-arrow-color': 'red',
                    'target-arrow-shape': 'triangle',
                    'line-color': '#ff6f5c'
                }
        },
        {
                'selector': '#AB',
                'style': {
                    'label': '0.5',
                    'text-rotation': 'autorotate',
                    'text-background-color': 'white',
                    'text-background-opacity': 1,
                    'text-background-padding': '4px'


                }
            },
          {
                'selector': '#BC',
                'style': {
                    'label': '0.88',
                     'text-rotation': 'autorotate',
                     'text-background-color': 'white',
                     'text-background-opacity': 1,
                     'text-background-padding': '4px'



                }
            },
]


