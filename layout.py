import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, Input, Output, State
import dash_auth
import datetime
lost_reason = ['Bad Weather', 'Scheduled observer team not available',
               'Problem with the telescope (e.g. drive system, active surface, M2, M3, etc.)',
               'Site problem (e.g. power, ice on dish, etc.)', 'Other']

instruments = ['rsr', 'sequoia', 'toltec', '1mm']

red_star_style = {"color": "red", 'marginRight': '5px'}

keyworks = ['Engineering', 'Telescope', 'M1', 'M2', 'M3', 'Actuators', 'TempSens', 'TolTEC', 'RSR', 'SEQUOIA', '1mm',
            'Pointing', 'Focus', 'Astigmatism', 'Error']

navbar = html.Div('Telescope Operation Log',
                  style={'textAlign': 'center', 'fontSize': '50px', 'marginBottom': '50px', 'marginTop': '20px',
                         'fontWeight': 'bold', 'color': 'white', 'backgroundColor': '#177199'})
cardheader_style = {'textAlign': 'center', 'backgroundColor': '#177199', 'color': 'white'}
operator_name_input = html.Div(
    [
        dbc.Label('Operator Name'),
        dbc.Input(id='operator-name-input', placeholder='Enter Operator Name', type='text'),
    ]
)

arrival_time_input = html.Div(
    [
        dbc.Label('Arrival Time'),
        dbc.Row([dbc.Col(dbc.Input(id='arrival-time-input', type='datetime-local', value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'))),
                 dbc.Col(html.Button("Now", id='arrive-now-btn', ))], align='end'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ]
)

shutdown_time_input = html.Div(
    [
        dbc.Label('Shutdown Time'),
        dbc.Row([dbc.Col(dbc.Input(id='shutdown-time-input', type='datetime-local',
                                   value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'))),
                 dbc.Col(html.Button("Now", id='showdown-now-btn', ))], align='end'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ])

problem_log_time_input = html.Div(
    [
        dbc.Label('Log Time'),
        dbc.Row([
            dbc.Col(dbc.Input(id='problem-log-time', type='datetime-local', value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'))),
            dbc.Col(html.Button("Now", id='problem-log-now-btn', ))], align='end'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ]
)

restart_time_input = html.Div(
    [
        dbc.Label('Restart Time'),
        dbc.Row([dbc.Col(dbc.Input(id='restart-time-input', type='datetime-local',
                                   value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'))),
                 dbc.Col(html.Button("Now", id='restart-now-btn',))], align='end'),
        dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
    ])

operator_arrive = dbc.Card(
    [
        dbc.CardHeader(html.H5("Arrival"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(operator_name_input, width='auto'),
                        dbc.Col(arrival_time_input),
                    ],
                    align='start', justify='start', className='mb-3'
                ),
                dbc.Row(dbc.Col(html.Button("Save Operator's Name and arrival Time", id='arrival-btn', n_clicks=0,
                                            className='save-button'),width='auto'),align='center', justify='center')
            ]
        )
    ],
    className='mb-4'
)


shutdown_time = dbc.Card([
    dbc.CardHeader(html.H5("Shutdown"), style=cardheader_style),
    dbc.CardBody([
        shutdown_time_input,
dbc.Row(dbc.Col(html.Button('Save Shutdown Time', id='shutdown-btn', n_clicks=0, className='save-button'), width='auto'),
        align='center', justify='center', className='mt-3')
    ]),])

instrument_status = dbc.Card(
    [
        dbc.CardHeader(html.H5("Facility Instruments Ready"), style=cardheader_style),
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
                dbc.Row(dbc.Col(html.Button("Save Instruments' statuses", id='instrument-btn', className='save-button', n_clicks=0),width='auto'), align='center', justify='center')
            ]
        ),
    ], className='mb-4'
)

reasons = ['Observers', 'Weather', 'Icing', 'Power',  'Other']

problem_form = dbc.Card(
    [
        dbc.CardHeader(html.H5("Report A Problem"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(problem_log_time_input, className='mb-3'),
                html.Hr(),
                dbc.Label('Enter reasons for the problem', ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.FormText('Observers not available'),
                                dbc.Input(id=f"lost-{reasons[0].lower()}"),
                            ], width='4')
                    ] + [
                        dbc.Col(
                            [
                                dbc.FormText(label),
                                dbc.Input(id=f"lost-{label.lower()}"),
                            ], width='4'
                        ) for label in reasons[1:]
                    ] , align='start', justify='start'
                ),
                dbc.Row(dbc.Col(html.Button('Save Problem Time and Reasons', id='problem-btn', n_clicks=0, className='save-button'),
                                width='auto'), align='center', justify='center', className='mt-2')
            ]
        )
    ], className='mb-4 '
)

restart_form = dbc.Card(
    [
        dbc.CardHeader(html.H5("Restart"), style=cardheader_style),
        dbc.CardBody(
            [
                dbc.Row(restart_time_input,),
                dbc.Row(dbc.Col(html.Button('Save Restart Time', id='restart-btn', n_clicks=0, className='save-button'), width='auto'),
                        align='center', justify='center', className='mt-3')
            ]
        )
    ], className='mb-5 '
)
# label and input for the form (Weather, Icing, Power, Observer, Other)
obsNum_input = html.Div(
    [
        dbc.Row([dbc.Col(dbc.Input(id='obsnum-input'),),
                 dbc.Col(html.Button('Update', id='update-btn'), width='auto'),], ),
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
        dbc.CardHeader(html.H5("ObsNum",), style=cardheader_style),
        dbc.CardBody(
            [
                obsNum_input,
                html.Hr(),
                keywork_input,
                html.Hr(),
                dbc.Label('Entry'),
                dcc.Textarea(id='entry-input', placeholder='Enter entry here', style={'width': '100%', 'height': 30}),
                dbc.Row(dbc.Col(html.Button('Save Entry', id='entry-btn', n_clicks=0, className='save-button'), width='auto'),
                        align='center', justify='center', className='mt-1')
            ]
        )
    ], className='mb-3 '
)


