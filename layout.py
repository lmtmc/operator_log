import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, Input, Output, State
import dash_auth
import datetime
lost_reason = ['Bad Weather', 'Scheduled observer team not available',
               'Problem with the telescope (e.g. drive system, active surface, M2, M3, etc.)',
               'Site problem (e.g. power, ice on dish, etc.)', 'Other']

instruments = ['rsr', 'sequoia', 'toltec', 'one_mm']

red_star_style = {"color": "red", 'marginRight': '5px'}

#Navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Telescope Operation Log", className="ml-3"),  # Space at the beginning
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Row(
                    [
                        dbc.Col(dbc.NavLink("Enter Data", href="/enter-data", style={'color': 'white'}), width='auto'),
                        dbc.Col(dbc.NavLink("Search", href="/search", style={'color': 'white'}), width='auto'),
                        dbc.Col(dbc.NavLink("Report", href="/report", style={'color': 'white'}), width='auto'),
                        dbc.Col(
                            dbc.DropdownMenu(
                                label='Log',
                                nav=True,
                                in_navbar=True,
                                children=[
                                    dbc.DropdownMenuItem("Log History", id='history-button'),
                                    dbc.DropdownMenuItem("Download Log", id='download-button'),
                                ],
                                right=True,
                                style={'color': 'white'},  # Style for the dropdown menu
                            ),
                            width="auto",
                            className="mr-3"  # Space at the end of the navbar items
                        )
                    ],
                    className='mt-3 mt-md-0 flex-nowrap ms-auto',  # Alignment classes
                    align='center',
                    justify='end'
                ),
                id="navbar-collapse",
                navbar=True,
                is_open=True
            )
        ],
        fluid=True  # Set to True for a full-width container, False for a fixed-width container
    ),
    color="secondary",
    dark=True,
    className='mb-5 mt-5 ml-5 mr-5'  # Overall navbar padding
)

arrival_time = dbc.Card([
    dbc.CardHeader(html.H5("Log Arrival Time")),
    dbc.CardBody([
        dbc.Row(
            [
                dbc.Col(dcc.Input(type='datetime-local', id='arrival-time-input',
                              value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'),style={'marginRight': '5px'})),
                dbc.Col(dbc.Button('Save', id='arrival-btn', n_clicks=0, size='sm'))
             ],align='end', justify='end', ),
        ],
    ),], className='mb-5 card-container')


leave_time = dbc.Card([
    dbc.CardHeader(html.H5("Log Leave Time")),

    dbc.CardBody([
        dbc.Row(
            [
                dbc.Col(dcc.Input(type='datetime-local', id='leave-time-input', value=datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'))),
                dbc.Col(dbc.Button('Save', id='leave-btn', n_clicks=0, size='sm'))
            ]
        ),
    ]),], className='mb-5 card-container')

instrument_status = dbc.Card(
    [
        dbc.CardHeader(html.H5("Facility Instruments Ready")),
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
                        # Column for the save button
                        dbc.Col(
                            dbc.Button("Save", id='instrument-btn', size='sm')
                        )
                    ]
                )
            ]
        ),
    ], className='mb-5 card-container'
)

reasons = ['Observer', 'Weather', 'Icing', 'Power',  'Other']

problem_form = dbc.Card(
    [
        dbc.CardHeader(html.H5("Report A Problem")),
        dbc.CardBody(
            [
                dbc.Row(
                    [dbc.Col([dbc.Label("Log Time"), dbc.Input(type='datetime-local',id="problem-time")])] +
                    [
                        dbc.Col(
                            [
                                dbc.Label(label),
                                dbc.Input(id=f"lost-{label.lower()}"),
                            ],
                        ) for label in reasons
                    ] +
                    [
                        # Additional column for the buttons
                        dbc.Col(
                            [
                                dbc.Button('Report', id='report-problem-btn', className='me-2',size='md'),
                                dbc.Button('Fixed', id='fixed-btn', disabled=True, size='md'),
                            ],

                        )
                    ], align='end', justify='end'
                )
            ]
        )
    ]
)


# label and input for the form (Weather, Icing, Power, Observer, Other)




table_modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Log History")),
        dbc.ModalBody(
            html.Div(id='modal-body-content')  # Container for DataTable
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ml-auto")
        ),
    ],
    id="table-container",
    is_open=False,  # By default, the modal is not open
    size="xl",  # Optional: specify the size of the modal (e.g., "sm", "lg", "xl")
)

