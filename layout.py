import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, Input, Output, State
import dash_auth
import datetime
import dash_ag_grid as dag
from db import fetch_log_data, current_time_input
lost_reason = ['Bad Weather', 'Scheduled observer team not available',
               'Problem with the telescope (e.g. drive system, active surface, M2, M3, etc.)',
               'Site problem (e.g. power, ice on dish, etc.)', 'Other']

instruments = ['rsr', 'sequoia', 'toltec', '1mm']

red_star_style = {"color": "red", 'marginRight': '5px'}

keyworks = ['Engineering', 'Telescope', 'M1', 'M2', 'M3', 'Actuators', 'TempSens', 'TolTEC', 'RSR', 'SEQUOIA', '1mm',
            'Pointing', 'Focus', 'Astigmatism', 'Error']

navbar = html.Div(dbc.NavbarSimple(
    children = [
        dbc.NavItem(dbc.NavLink(id='login-name')),
        dbc.NavItem(dbc.NavLink(id='logout-btn',href='/logout')),
    ],
    brand="LMT Operator Log",
    brand_href="#",
    color='#177199',
    dark=True,),style={'marginBottom': '20px', 'backgroundColor': '#177199','width': '85%','marginLeft': 'auto', 'marginRight': 'auto'})


cardheader_style = {'textAlign': 'center', 'backgroundColor': '#177199', 'color': 'white'}
operator_name_input = html.Div(
    [
        dbc.Row(dbc.Label('Operator Name')),
        dbc.Row([
            dbc.Col(dbc.Input(id='operator-name-input', placeholder='Enter Operator Name', type='text'), width=10),
            dbc.Col(html.Button('x', id='clear-name-btn'))], align='center', justify='end', className='gx-1'),
    ]
)

arrival_time_input = html.Div(
    [
        dbc.Label('Arrival Time'),
        dbc.Row(
            [
                dbc.Col(dbc.Input(id='arrival-time-input', type='datetime-local', value=current_time_input())),
                dbc.Col(html.Button("Now", id='arrive-now-btn', ))
            ], align='center', justify='end', className='gx-1'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ]
)

shutdown_time_input = html.Div(
    [
        dbc.Label('Shutdown Time'),
        dbc.Row([dbc.Col(dbc.Input(id='shutdown-time-input', type='datetime-local',
                                   value=current_time_input())),
                 dbc.Col(html.Button("Now", id='showdown-now-btn', ))], align='center', justify='end', className='gx-1'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ])

problem_log_time_input = html.Div(
    [
        dbc.Label('Log Time'),
        dbc.Row([
            dbc.Col(dbc.Input(id='problem-log-time', type='datetime-local', value=current_time_input())),
            dbc.Col(html.Button("Now", id='problem-log-now-btn', ))], align='center', justify='end', className='gx-1'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ]
)

restart_time_input = html.Div(
    [
        dbc.Label('Restart Time'),
        dbc.Row([dbc.Col(dbc.Input(id='restart-time-input', type='datetime-local',
                                   value=current_time_input())),
                 dbc.Col(html.Button("Now", id='restart-now-btn',))], align='center', justify='end', className='gx-1'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ])

operator_arrive = dbc.Card(
    [
        # dbc.CardHeader(html.H5("Arrival"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(operator_name_input,width=5),
                        dbc.Col(arrival_time_input, width=7),
                    ],
                    align='start', justify='start', className='mb-3'
                ),
                dbc.Row(dbc.Col(html.Button("SAVE", id='arrival-btn', n_clicks=0,
                                            className='save-button'),width='auto'),align='center', justify='center')
            ]
        )
    ],
    className='mb-4'
)


shutdown_time = dbc.Card([
    # dbc.CardHeader(html.H5("Shutdown"), style=cardheader_style),
    dbc.CardBody([
        shutdown_time_input,
dbc.Row(dbc.Col(html.Button('SAVE', id='shutdown-btn', n_clicks=0, className='save-button'), width='auto'),
        align='center', justify='center', className='mt-3')
    ]),])

instrument_status = dbc.Card(
    [
        # dbc.CardHeader(html.H5("Facility Instruments Ready"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        # Column for the checklist
                        dbc.Col(
                            dbc.Checklist(
                                id=instruments[0],
                                options=[{'label': instruments[0], 'value': 1}], switch=True, inline=True
                            )
                        ),
                        dbc.Col(dbc.Checklist(id=instruments[1],options=[{'label': instruments[1], 'value': 1}],switch=True,inline=True)),
                        dbc.Col(dbc.Checklist(id=instruments[2],options=[{'label': instruments[2], 'value': 1}],switch=True,inline=True)),
                        dbc.Col(dbc.Checklist(id=instruments[3],options=[{'label': instruments[3], 'value': 1}],switch=True,inline=True)),


                    ], className='mb-3', align='center', justify='center'
                ),
                dbc.Row(dbc.Col(html.Button("SAVE", id='instrument-btn', className='save-button', n_clicks=0),width='auto'), align='center', justify='center')
            ]
        ),
    ], className='mb-4'
)

reasons = ['Weather', 'Icing', 'Power',  'Observers', 'Other']

problem_form = dbc.Card(
    [
        # dbc.CardHeader(html.H5("Report A Problem"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(problem_log_time_input, className='mb-3'),
                html.Hr(),
                dbc.Label('Enter reasons for the problem', ),
                dbc.Row(
                    [
                    dbc.Col(
                            [
                                dbc.FormText(reasons[0]),
                                dbc.Input(id=f"lost-{reasons[0].lower()}"),
                            ], width='4'
                        ),
                    dbc.Col(
                            [
                                dbc.FormText(reasons[1]),
                                dbc.Input(id=f"lost-{reasons[1].lower()}"),
                            ], width='4'
                        ),
                    dbc.Col(
                        [
                            dbc.FormText(reasons[2]),
                            dbc.Input(id=f"lost-{reasons[2].lower()}"),
                        ], width='4'
                    ),
                    dbc.Col(
                        [
                            dbc.FormText('Observers Not Available'),
                            dbc.Input(id=f"lost-{reasons[3].lower()}"),
                        ], width='4'
                    ),
                    dbc.Col(
                            [
                                dbc.FormText(reasons[4]),
                                dbc.Input(id=f"lost-{reasons[4].lower()}"),
                            ], width='4'
                        )
                    ] , align='start', justify='start'
                ),
                dbc.Row(dbc.Col(html.Button('SAVE', id='problem-btn', n_clicks=0, className='save-button'),
                                width='auto'), align='center', justify='center', className='mt-2')
            ]
        )
    ], className='mb-4 '
)

restart_form = dbc.Card(
    [
        # dbc.CardHeader(html.H5("Restart"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(restart_time_input,),
                dbc.Row(dbc.Col(html.Button('SAVE', id='restart-btn', n_clicks=0, className='save-button'), width='auto'),
                        align='center', justify='center', className='mt-3')
            ]
        )
    ], className='mb-5 '
)
# label and input for the form (Weather, Icing, Power, Observer, Other)
obsNum_input = html.Div(
    [
        dbc.Row([dbc.Col(dbc.Input(id='obsnum-input'),),
                 dbc.Col(html.Button('Update', id='update-btn'), width='auto'),],align='center', justify='end', className='gx-1' ),
        dbc.FormText("Enter as a list of values ObsNum1, ObsNum2, ... where each ObsNum is a number or a range in the form n1-n2 "
                     "OR push the Update button to get ObsNum from the system", color="secondary"),
    ],
)
keywork_input = html.Div(
    [
        dbc.Label('Enter keyword below and/or select from list', ),
        dbc.Row([
            dbc.Col(dbc.Input(id='keyword-input', type='text', placeholder='Enter keyword'), width=3),
            dbc.Col(dbc.Checklist(id='keyword-checklist', options=[{'label': key, 'value': key} for key in keyworks],
                                  inline=True, className='custom-checklist'), width=9),
        ])
    ],
)


ObsNum_form = dbc.Card(
    [
        # dbc.CardHeader(html.H5("ObsNum",), style=cardheader_style),
        dbc.CardBody(
            [
                obsNum_input,
                html.Hr(),
                keywork_input,
                html.Hr(),
                dbc.Label('Entry'),
                dcc.Textarea(id='entry-input', placeholder='Enter entry here', style={'width': '100%', 'height': 30}),
                dbc.Row(dbc.Col(html.Button('SAVE', id='entry-btn', n_clicks=0, className='save-button'), width='auto'),
                        align='center', justify='center', className='mt-1')
            ]
        )
    ], className='mb-3 '
)


columnDefs = [
    {
        "headerName": "Log Details",
        "children": [
            {"field": "ID",  "pinned": 'left'},
            {"field": "Timestamp", "pinned": 'left'},
            {"field": "Operator Name",  "pinned": 'left'},
        ]
    },

    {
        "headerName": "Operation Times",
        "children": [
            {"field": "Arrival Time", },
            {"field": "Shutdown Time", "columnGroupShow": "open"},
            {"field": "Lost Time", "columnGroupShow": "open"},
            {"field": "Restart Time", "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "Instruments",
        "children": [
            {"field": "RSR",},
            {"field": "SEQUOIA", "columnGroupShow": "open"},
            {"field": "TolTEC", "columnGroupShow": "open"},
            {"field": "1mm", "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "Lost Details",
        "children": [
            {"field": "Weather"},
            {"field": "Icing", "columnGroupShow": "open"},
            {"field": "Power", "columnGroupShow": "open"},
            {"field": "Observers Not Available", "columnGroupShow": "open"},
            {"field": "Others", "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "Observation",
        "children": [
            {"field": "ObsNum"},
            {"field": "Keyword", "columnGroupShow": "open"},
            {"field": "Entry", "columnGroupShow": "open"},
        ],
    }
]
log_history = dbc.Card(
            [
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H5("Log History (10 most recent entries)"), style={'textAlign': 'center'},
                                ),
                        dbc.Col(html.Button('Download Log', id='download-button', n_clicks=0, className='download-button'),
                                width='auto'),
                    ], align='center', justify='center', className='mt-3')]),
                dbc.CardBody(
                    [
                        html.Div(dag.AgGrid(
                            id='log-table',
                            rowData=fetch_log_data(10),
                            columnDefs=columnDefs,
                            defaultColDef={'filter': True, 'resizable': True},
                            columnSize='autoSize',
                        ), className='mt-3 ml-5  ', id='status-container'),
                    ]
                )
            ], className='mt-5 mb-5'
        ),

input_select = html.Div(
    dbc.Tabs([
        dbc.Tab(operator_arrive, label='Arrival', tab_id='tab-arrive'),
        dbc.Tab(restart_form, label='Restart'),
        dbc.Tab(shutdown_time, label='Shutdown'),
        dbc.Tab(instrument_status, label='Instruments'),
        dbc.Tab(problem_form, label='Problem'),
        dbc.Tab(ObsNum_form, label='ObsNum'),

    ], id='tabs'),className='form-container'
)

dash_app_page = dbc.Container([
    input_select,
    html.Div(log_history),
    dcc.Download(id='download-log')
])

login_page = dbc.Container([
            dbc.Row(dbc.Col(dbc.Input(id='username', placeholder='Username',className='mb-3'),width=4), justify='center'),
            dbc.Row(dbc.Col(dbc.Input(id='password', placeholder='Password', type='password'), width=4), justify='center'),
            dbc.Row(dbc.Col(dbc.Button('Login', id='login-btn', n_clicks=0),width='auto'), justify='center', className='mt-3'),
        ])