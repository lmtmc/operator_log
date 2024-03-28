import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, Input, Output, State
import dash_auth
import datetime
import dash_ag_grid as dag
from db import (fetch_log_data, current_time, fetch_all_users, add_user, data_column,
                update_user_password, fetch_user_by_username, exist_user, exist_email, validate_user,fetch_all_users)

prefix = 'operator_log'

lost_reason = ['Bad Weather', 'Scheduled observer team not available',
               'Problem with the telescope (e.g. drive system, active surface, M2, M3, etc.)',
               'Site problem (e.g. power, ice on dish, etc.)', 'Other']


instruments = ['TolTEC', 'RSR', 'SEQUOIA', '1mm']

red_star_style = {"color": "red", 'marginRight': '5px'}

keyworks = ['Engineering', 'Telescope', 'M1', 'M2', 'M3', 'Actuators', 'TempSens', 'TolTEC', 'RSR', 'SEQUOIA', '1mm',
            'Pointing', 'Focus', 'Astigmatism', 'Error']

navbar = html.Div(dbc.NavbarSimple(
    children = [
        dbc.NavItem(dbc.NavLink('Home', href=f'/{prefix}')),
        dbc.NavItem(dbc.NavLink(id='login-name')),
        # dbc.NavItem(dbc.NavLink(id='login-btn',href=f'/{prefix}/login')),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("Settings", id='setting-btn', href=f"/{prefix}/settings"),
                dbc.DropdownMenuItem("Logout", id='logout-btn', href=f"/{prefix}/logout"),],
            nav=True, in_navbar=True, right=True, id='user-dropdown'),
        ],
    brand="LMT Observer Log",
    brand_href="#",
    color='#177199',
    dark=True,
    id='navbar'),
    style={'backgroundColor': '#177199'}
)

cardheader_style = {'textAlign': 'center'}
cardbody_style = {'height': '410px', 'overflowY': 'auto'}
cardfooter_style = {'textAlign': 'right'}
# arrival page 1. observers name component
observers = html.Div(
    [
            dbc.Row([
                dbc.Col(dbc.Label('Select Observers'), width=2),
                dbc.Col([
                    dbc.Row(
                        [
                            dbc.Col(dbc.Checklist(id='observers-checklist',inline=True,), width='auto'),
                            dbc.Col(dbc.Input(id='observer-name-input', type='text', placeholder='Enter additional observer',
                                    ), width='auto')
                        ], align='center'
                    ),
                ]),
            ], className='mt-3'),
])

# arrival page 2. arrival time component
arrival_time_input = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Arrival Time'), width=2),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(dbc.Input(id={'type':'dynamic-time-input','index':'arrival-time-input'}, type='datetime-local', value=current_time())),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn','index':'arrival-time-input'}, ))
                        ], align='center', justify='end', className='gx-1'),
                    dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
                ]
            )]),
    ]
)

# Arrival page 3. weather component
arrival_weather = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Weather Condition'), width=2),

            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Input(id={'type':'dynamic-time-input','index':'weather-time-input'}, type='datetime-local', )),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn','index':'weather-time-input'}, ))
                        ], align='center', justify='end', className='gx-1'),
                    dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary"),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col([dbc.Label('Sky'), dbc.Input(id='sky-input')]),
                            dbc.Col([dbc.Label('Tau'), dbc.Input(id='tau-input')]),
                            dbc.Col([dbc.Label('T'), dbc.Input(id='t-input')]),
                            dbc.Col([dbc.Label('RH'), dbc.Input(id='rh-input')]),
                            dbc.Col([dbc.Label('Wind'), dbc.Input(id='wind-input')]),
                            dbc.Col([dbc.Label('Other'), dbc.Input(id='weather-other-input')]),
                        ], align='center'
                    ),
                ]
            ),
        ]),
    ]
)

# arrival page #4 Main Plan
main_plan = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Main Plan'), width=2),
            dbc.Col(dbc.Input(id='main-plan-input', placeholder='Enter main plan here', style={'width': '100%'}), ),
        ], className='mt-3')
    ]
)
# arrival page
observer_arrive = dbc.Card([
        dbc.CardHeader(html.H5(id='observer-name-label', style=cardheader_style)),
        dbc.CardBody(
            [
                observers,
                html.Br(),
                arrival_time_input,
                html.Br(),
                arrival_weather,
                html.Br(),
                main_plan,
            ],style=cardbody_style
        ),
    dbc.CardFooter(
        html.Div(html.Button("SAVE", id='arrival-btn', n_clicks=0,className='save-button'),style=cardfooter_style)
    )],
)

# instrument page 1 instrument start time component
instrument_time_input = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('System Start Time'), width=2),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(dbc.Input(id={'type':'dynamic-time-input','index':'start-time-input'}, type='datetime-local')),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn','index':'start-time-input'}, ))
                        ], align='center', justify='end', className='gx-1'),
                    dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
                ]
            )]),
    ]
)

# instrument page 2 instrument status component
instrument_status = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Initial Setup'), width=2),
            dbc.Col(
                [
                    dbc.Row(
                        [dbc.Col(dbc.Checklist(
                                id=instrument,
                                options=[{'label': f'{instrument} ready', 'value': 1}],
                                inline=True,
                            ),width=3),  # Adjust width as needed
                            dbc.Col(dbc.Input(id={'type':'dynamic-time-input','index':f'{instrument}-time-input'}, type='datetime-local', ),width='auto'),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn', 'index':f'{instrument}-time-input'}),width='auto'),

                            dbc.Col(dbc.Input(id=f'{instrument}-note', placeholder="Note"), width=4),  # Adjust width as needed
                        ],
                        className='mb-3',  # Adds margin-bottom
                        align='center',  # Vertically center the items in the row
                    ) for instrument in instruments
                ]
            ),
        ]),
    ],
)

# Instrument page 3 Notes
instrument_notes =  html.Div(dbc.Row(
            [
                dbc.Col(dbc.Label('Notes'), width=2),
                dbc.Col(dbc.Input(id='instrument-note', placeholder='Enter note here',
                                  style={'width': '100%'}), ),
            ], className='mt-3'
        ))

instrument_form = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(html.H5("Instrument Setup", style=cardheader_style)),
                dbc.CardBody(
                    [
                        instrument_time_input,
                        html.Br(),
                        instrument_notes,
                        html.Br(),
                        instrument_status,
                    ],style=cardbody_style
                ),
                dbc.CardFooter(
                    html.Div(html.Button('SAVE', id='instrument-btn', n_clicks=0, className='save-button'),style=cardfooter_style)
                )
    ]
)])

shutdown_time_input = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Shutdown Time',), width=2),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(dbc.Input(id={'type':'dynamic-time-input','index':'shutdown-time-input'}, type='datetime-local', )),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn','index':'shutdown-time-input'}, ))
                        ], align='center', justify='end', className='gx-1'),
                    dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
                ]
            )],),
    ]
)
problem_log_time_input = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Log Time',), width=2),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(dbc.Input(id={'type':'dynamic-time-input','index':'problem-log-time'}, type='datetime-local',)),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn','index':'problem-log-time'}, ))
                        ], align='center', justify='end', className='gx-1'),
                    dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
                ]
            )],),
    ]
)
resume_time_input = html.Div(
    [
        dbc.Row([
            dbc.Col(dbc.Label('Resume Time'), width=2),
            dbc.Col(
                [
                    dbc.Row(
                        [
                            dbc.Col(dbc.Input(id={'type':'dynamic-time-input','index':'resume-time-input'}, type='datetime-local', )),
                            dbc.Col(html.Button("Now", id={'type':'dynamic-time-now-btn','index':'resume-time-input'}, ))
                        ], align='center', justify='end', className='gx-1'),
                    dbc.FormText("Enter time manually or push 'Now' to use current time", color="secondary")
                ]
            )]),
    ]
)


shutdown_time = dbc.Card([
    dbc.CardHeader(html.H5("Shutdown", style=cardheader_style)),
    dbc.CardBody(shutdown_time_input,style=cardbody_style),
    dbc.CardFooter(
        html.Div(html.Button('SAVE', id='shutdown-btn', n_clicks=0, className='save-button'),style=cardfooter_style)),])

reasons = ['Weather', 'Icing', 'Power',  'Observers', 'Other']
problem_reasons = html.Div(
    dbc.Row([
        dbc.Col(dbc.Label('Enter reasons'), width=2),  # This is the label column
        dbc.Col([
            dbc.Row(
                [
                    dbc.Col(dbc.Row([dbc.FormText(reasons[0]), dbc.Input(id=f"lost-{reasons[0].lower()}")]), className='mx-2'),
                    dbc.Col(dbc.Row([dbc.FormText(reasons[1]), dbc.Input(id=f"lost-{reasons[1].lower()}")]),className='mx-2'),
                    dbc.Col(dbc.Row([dbc.FormText(reasons[2]), dbc.Input(id=f"lost-{reasons[2].lower()}")]),className='mx-2'),
                    dbc.Col(dbc.Row([dbc.FormText('Observers Not Available'), dbc.Input(id=f"lost-{reasons[3].lower()}")]),className='mx-2'),
                ], align='center',
            ),
           dbc.Row(dbc.Col([dbc.FormText(reasons[4]), dbc.Input(id=f"lost-{reasons[4].lower()}")],), ),]
        ),
    ],  )
)

problem_form = dbc.Card(
    [
        dbc.CardHeader(html.H5("Pause or Cancellation", style=cardheader_style)),
        dbc.CardBody(
            [
                dbc.Row(problem_log_time_input, className='mb-3'),
                problem_reasons,
            ],style=cardbody_style
        ),
        dbc.CardFooter(html.Div(html.Button('SAVE', id='problem-btn', n_clicks=0, className='save-button'),style=cardfooter_style,))
    ]
)

resume_form = dbc.Card(
    [
        dbc.CardHeader(html.H5("Resume", style=cardheader_style)),
        dbc.CardBody(
            [
                resume_time_input,
                dbc.Row(
                    [
                        dbc.Col(dbc.Label('Comment'), width=2),
                        dbc.Col(dbc.Input(id='resume-comment', placeholder='Enter comment here',
                                             style={'width':'100%'}), ),
                    ], className='mt-3'),
            ],style=cardbody_style),
        dbc.CardFooter(html.Div(html.Button('SAVE', id='resume-btn', n_clicks=0, className='save-button'),style=cardfooter_style))
    ],
)
# label and input for the form (Weather, Icing, Power, Observer, Other)
obsNum_input = html.Div(
    [
        dbc.Row([dbc.Col(dbc.Input(id='obsnum-input'),),
                 #dbc.Col(html.Button('Update', id='update-btn'), width='auto'),
                 ],align='center', justify='end', className='gx-1'
                ),
        # dbc.FormText("Enter as a list of values ObsNum1, ObsNum2, ... where each ObsNum is a number or a range in the form n1-n2 "
        #              "OR push the Update button to get ObsNum from the system", color="secondary"),
        dbc.FormText("Enter as a list of values ObsNum1, ObsNum2, ... where each ObsNum is a number or a range in the form n1-n2 "
                     ,color="secondary"),
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
        dbc.CardHeader(html.H5("User Note",), style=cardheader_style),
        dbc.CardBody(
            [
                obsNum_input,
                html.Br(),
                keywork_input,
                dbc.Label('Entry'),
                dbc.Input(id='entry-input', placeholder='Enter entry here'),
            ],style=cardbody_style
        ),
        dbc.CardFooter(
            html.Div(html.Button('SAVE', id='note-btn', n_clicks=0, className='save-button'), style=cardfooter_style))
    ], className='mb-3 '
)

columnDefs = [
    {"field": data_column[0]},
    {"field": data_column[1]},
    {
        "headerName": "Observers",
        "children": [
            {"field": data_column[2], },
            {"field": data_column[3], "columnGroupShow": "open"},
            {"field": data_column[4], "columnGroupShow": "open"},
            {"field": data_column[5],"columnGroupShow": "open"},
        ]
    },
    {
        "headerName": "Weather",
        "children": [
            {"field": data_column[6],},
            {"field": data_column[7], "columnGroupShow": "open"},
            {"field": data_column[8], "columnGroupShow": "open"},
            {"field": data_column[9], "columnGroupShow": "open"},
            {"field": data_column[10], "columnGroupShow": "open"},
            {"field": data_column[11], "columnGroupShow": "open"},
            {"field": data_column[12], "columnGroupShow": "open"},
        ]
    },
    { "field": data_column[13]},
    {
        "headerName": "Instruments",
        "children": [
            {"field": data_column[14],},
            {"field": data_column[15], "columnGroupShow": "open"},
            {"field": data_column[16], "columnGroupShow": "open"},
            {"field": data_column[17], "columnGroupShow": "open"},
            {"field": data_column[18], "columnGroupShow": "open"},
            {"field": data_column[19], "columnGroupShow": "open"},
            {"field": data_column[20], "columnGroupShow": "open"},
            {"field": data_column[21], "columnGroupShow": "open"},
            {"field": data_column[22], "columnGroupShow": "open"},
            {"field": data_column[23], "columnGroupShow": "open"},
            {"field": data_column[24], "columnGroupShow": "open"},
            {"field": data_column[25], "columnGroupShow": "open"},
            {"field": data_column[26], "columnGroupShow": "open"},
            {"field": data_column[27], "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "Problem Details",
        "children": [
            {"field": data_column[28]},
            {"field": data_column[29], "columnGroupShow": "open"},
            {"field": data_column[30], "columnGroupShow": "open"},
            {"field": data_column[31], "columnGroupShow": "open"},
            {"field": data_column[32], "columnGroupShow": "open"},
            {"field": data_column[33], "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "Resume Details",
        "children": [
            {"field": data_column[34]},
            {"field": data_column[35], "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "User Notes",
        "children": [
            {"field": data_column[36]},
            {"field": data_column[37], "columnGroupShow": "open"},
            {"field": data_column[38], "columnGroupShow": "open"},
        ],
    },
    {
        "headerName": "Shutdown",
        "children": [
            {"field": data_column[39]},
        ],
    }
]
log_history = html.Div(
            [
                dbc.Row([
                    dbc.Col(dbc.Button("View Log History ", id="view-btn",className='download-button'),width='auto'),
                    dbc.Col(html.Button('Download Log', id='download-button', n_clicks=0, className='download-button'),width='auto'),
                ],  className='mt-3'),

                html.Div(dag.AgGrid(
                            id='log-table',
                            rowData=fetch_log_data(10),
                            columnDefs=columnDefs,
                            defaultColDef={'filter': True, 'resizable': True},
                            columnSize='sizeToFit',

                        ), className='mt-3 ml-5  ', id='log-table-div', style={'display': 'none'}),


            ], className='mt-5 mb-5'
        ),
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '30px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#177199',
    'color': 'white',
    'padding': '30px'
}
tab_select = html.Div(dbc.Row([
    dbc.Col(html.Div(
        [
            dcc.Tabs(
            children=[
            dcc.Tab(label='Arrival', value='tab-arrive', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Instruments', value='tab-instrument', style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Pause or Cancellation', value='tab-problem',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Resume', value='tab-resume',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='User Note', value='tab-obsnum',style=tab_style, selected_style=tab_selected_style),
            dcc.Tab(label='Shutdown', value='tab-shutdown',style=tab_style, selected_style=tab_selected_style),
        ], id='tabs',vertical=True, value = 'tab-arrive', ),
    ], ), width='auto',),
    dbc.Col(html.Div(id='tab-content'))
],))

dash_app_page = dbc.Container([
    tab_select,
    html.Div(log_history),
    dcc.Download(id='download-log')
])

login_page = html.Div([
    html.H2('Login' , style={'textAlign': 'center'} ),
    html.Div([
    dbc.Label('Username', className='mt-4', style={'fontWeight': '500'}),
    dbc.Input(id='username', placeholder='Enter your username', className='mb-4', style={'borderRadius': '20px'}),
    dbc.Label('Password', style={'fontWeight': '500'}),
    dbc.Input(id='password', placeholder='Enter your password', type='password', className='mb-4', style={'borderRadius': '20px'}),
    dbc.Row([
        dbc.Col(
            dbc.Button('LOGIN', id='login-btn', n_clicks=0, color='primary', className='save-button ml-5',
                       #style={'width': '50%', 'borderRadius': '20px', 'padding': '10px'}
                       ),
            width={'offset': 4}
        )
    ]),
    html.Br(),
    html.Div(dbc.Alert(id='login-status', color='dark', is_open=False, dismissable=True,duration=4000,
                       style={'textAlign': 'center'}) ),
        ],className='login-container mt-1',
    )])


register_page = html.Div([
    dbc.Label('Username', className='mt-4', style={'fontWeight': '500'}),
    dbc.Input(id='register-username', placeholder='Enter your username', className='mb-4', style={'borderRadius': '20px'}),
    dbc.Label('Email', style={'fontWeight': '500'}),
    dbc.Input(id='register-email', placeholder='Enter your email', className='mb-4', style={'borderRadius': '20px'}),
    dbc.Label('Password', style={'fontWeight': '500'}),
    dbc.Input(id='register-password', placeholder='Enter your password', type='password', className='mb-4', style={'borderRadius': '20px'}),
    dbc.Label('Confirm Password', style={'fontWeight': '500'}),
    dbc.Input(id='register-confirm-password', placeholder='Confirm your password', type='password', className='mb-4', style={'borderRadius': '20px'}),
    dbc.Row([
        dbc.Col(
            dbc.Button('Register', id='register-btn', n_clicks=0, color='primary', className='mt-2',
                       style={'width': '100%', 'borderRadius': '20px', 'padding': '10px'}),
            width=12
        )
    ]),
    html.Br(),
    html.Div(dbc.Alert(id='register-status', color='dark', is_open=False, dismissable=True,
                       duration=4000, style={'textAlign': 'center'})),
        ],
    style={'maxWidth': '400px', 'margin': '40px auto', 'padding': '20px'})

login_tab = html.Div(login_page,className='login-container')


setting_page = html.Div([
    # Center the H2 element
    html.H2('Reset Account Password', style={'textAlign': 'center'}),

    dbc.Input(id='reset-password', placeholder='New Password', type='password', className='mb-3'),
    dbc.Input(id='reset-confirm-password', placeholder='Confirm Password', type='password', className='mb-3'),
    html.Div(dbc.Alert(id='reset-status', color='dark', is_open=False, dismissable=True,), style={'textAlign': 'center'}),

    # Use justify='center' to center the row's content
    dbc.Row(
        dbc.Col(
            dbc.Button('Reset Password', id='reset-btn', n_clicks=0, className='mb-3', color='secondary',
style={'width': '100%'}
                       ),

        ),
        justify='center',  # Center the content of Row
    ),
    dbc.Row(
        dbc.Col(
            dbc.Button('Cancel', id='back-btn', n_clicks=0, className='mb-3', color='secondary',
style={'width': '100%'}
                      ),

        ),
        justify='center',  # Center the content of Row
    ),
], className='login-container')

# add delete or modify the username and password
user_columnDefs = [
    {"field": "ID", "checkboxSelection":{"function": "params.data.Username !== 'admin'"}},
    {"field": "Username"},
    {"field": "Email"},
    {"field": "Is Admin"},
    {"field": "Created At"},]

user_details = dbc.Card(
            [
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H5("Users Management"), style={'textAlign': 'center'},),
                    ], align='center', justify='center', className='mt-3')]),
                dbc.CardBody(
                    [
                        html.Div(dag.AgGrid(
                            id='user-table',
                            rowData=fetch_all_users(),
                            columnDefs=user_columnDefs,
                            defaultColDef={'filter': True, 'resizable': True},
                            dashGridOptions={
                                #'rowSelection':"multiple",
                                             "suppressRowClickSelection": True, "animateRows": False,
                                             "undoRedoCellEditing": True,
                                             "undoRedoCellEditingLimit": 20,
                                             },
                            columnSize='autoFill',
                        ), className='mt-3 ml-5  '),
                    ]
                ),
                dbc.CardFooter(
                    dbc.Row([
                        dbc.Col(dbc.Button('Add User', id='add-user-btn', n_clicks=0, className='add-user-button'), width='auto'),
                        dbc.Col(dbc.Button('Delete User', id='delete-user-btn', n_clicks=0, className='delete-user-button',disabled=True), width='auto'),
                        #dbc.Col(dbc.Button('Update User', id='update-user-btn', n_clicks=0, className='update-user-button',disabled=True), width='auto'),
                    ], className='mt-3')
                )
            ], className='mt-5 mb-5'
        ),
admin_add_user = dbc.Modal(
    [
        dbc.ModalHeader(dbc.Label('Add A New User', style={'textAlign': 'center', 'fontWeight': 'bold'})),
        dbc.ModalBody(
            [
                dbc.Label('Username', className='mt-4', style={'fontWeight': '500'}),
                dbc.Input(id='add-username', placeholder='Enter username', className='mb-4', style={'borderRadius': '20px'}),
                dbc.Label('Email', style={'fontWeight': '500'}),
                dbc.Input(id='add-email', placeholder='Enter email', className='mb-4', style={'borderRadius': '20px'}),
                dbc.Label('Is Admin', style={'fontWeight': '500'}),
                dbc.Checklist(id='add-is-admin', options=[{'label': 'Yes', 'value': 1}], switch=True, inline=True, className='mb-4'),
                dbc.Label('Password', style={'fontWeight': '500'}),
                dbc.Input(id='add-password', placeholder='Enter password', type='password', className='mb-4', style={'borderRadius': '20px'}),
                dbc.Label('Confirm Password', style={'fontWeight': '500'}),
                dbc.Input(id='add-confirm-password', placeholder='Confirm password', type='password', className='mb-4', style={'borderRadius': '20px'}),
            ]
        ),
        dbc.ModalFooter(
            dbc.Button('Add', id='add-user', n_clicks=0, color='primary', className='mt-2',),
        ),
        html.Div(
            dbc.Alert(id='add-user-status', color='dark', is_open=False, dismissable=True, duration=4000, style={'textAlign': 'center'}),
            style={'maxWidth': '400px', 'margin': 'auto'}
        )
    ],
    id='add-user-modal',
    is_open=False,
    # style={'maxWidth': '400px', 'margin': '100px', 'padding': '20px', 'display': 'flex','justifyContent': 'center'}
)

admin_update_user = dbc.Modal(
    [
        dbc.ModalHeader(dbc.Label('Modify User', style={'textAlign': 'center', 'fontWeight': 'bold'})),
        dbc.ModalBody(
            [
                dbc.Label('Username', className='mt-4', style={'fontWeight': '500'}),
                dbc.Input(id='update-username', placeholder='Enter username', className='mb-4', style={'borderRadius': '20px'}),
                dbc.Label('Email', style={'fontWeight': '500'}),
                dbc.Input(id='update-email', placeholder='Enter email', className='mb-4', style={'borderRadius': '20px'}),
                dbc.Label('Is Admin', style={'fontWeight': '500'}),
                dbc.Checklist(id='update-is-admin', options=[{'label': 'Yes', 'value': 1}], switch=True, inline=True, className='mb-4'),
                dbc.Label('New Password', style={'fontWeight': '500'}),
                dbc.Input(id='update-password', placeholder='Enter password', type='password', className='mb-4', style={'borderRadius': '20px'}),
                dbc.Label('Confirm New Password', style={'fontWeight': '500'}),
                dbc.Input(id='update-confirm-password', placeholder='Confirm password', type='password', className='mb-4', style={'borderRadius': '20px'}),
            ]
        ),
        dbc.ModalFooter(
            dbc.Button('Save', id='update-user', n_clicks=0, color='primary', className='mt-2',),
        ),
        html.Div(
            dbc.Alert(id='update-user-status', color='dark', is_open=False, dismissable=True, duration=4000, style={'textAlign': 'center'}),
            style={'maxWidth': '400px', 'margin': 'auto'}
        )
    ],
    id='update-user-modal',
    is_open=False,
    # style={'maxWidth': '400px', 'margin': '100px', 'padding': '20px', 'display': 'flex','justifyContent': 'center'}
)

admin_page = dbc.Container(
    [
        html.Div([
            dbc.Button('Manage Users', id='manage-users-btn', n_clicks=0, className='mb-3', color='secondary',)]
                 ),

        html.Div(user_details, style={'display': 'none'}, id='user-details'),
        html.Div(admin_add_user),
        html.Div(admin_update_user),
        html.Div(dbc.Alert(id='admin-status', color='dark', is_open=False, dismissable=True,), style={'textAlign': 'center'}),
        ])
