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

status_update = html.Div(
    [
        html.Div(id='arrival-status', className='mb-3'),
        html.Div(id='instrument-status', className='mb-3'),
        html.Div(id='problem-status', className='mb-3'),
        html.Div(id='fixed-status', className='mb-3'),
        html.Div(id='leave-status'),
    ], className='mt-3, form-container', id='status-container', style={'display': 'none', 'height': '500px'})


arrival_time = html.Div(
    [
        dbc.Button("Arrive", n_clicks=0, className='large-button',id='arrival-btn'),
        dbc.Button('Report A Problem', id='report-problem-btn', className='large-button', disabled=True),
        dbc.Button('Leave', n_clicks=0, className='large-button', id ='leave-btn', disabled=True),
    ],className='mb-5 centered-div'
)

instrument_status = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(html.H5("Facility Instruments Ready")),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col([
                                    dbc.Checklist(
                                        id=instrument,
                                        options=[{'label': instrument, 'value': 1}],
                                        switch=True,
                                        inline=True
                                    )
                                ]) for i, instrument in enumerate(instruments)
                    ]
                )

                ]),
            dbc.CardFooter(html.Div(dbc.Button('submit', id='instrument-status-btn', className='mt-3'),
                                    className='right-aligned-buttons'))
        ]),
    ],
    id='instrument-status-check',style={'display':'none'}, className='mb-5')


labels = ['Weather', 'Icing', 'Power', 'Observer', 'Other']
reason_form1 = html.Div(
    [
        dbc.Label('Reasons'),
        dbc.Checklist(
                options=[{'label': i, 'value': i} for i in lost_reason],
                id='reason-input', inline=True
            ),
        html.Div(
                [
                    html.Span("*", style=red_star_style),
                    'Other Reason',
                    dbc.Textarea(id='other-reason')
                ],
                id='note-display', style={'display': 'none'}
            ),
])

reason_form2 =dbc.Card(
        [
            dbc.CardHeader(html.H5("Report Problem")),
            dbc.CardBody(
                [
                    dbc.Row(
                    [dbc.Col(
                        [
                            dbc.Col(dbc.Label(label), ),
                            dbc.Col(dbc.Input(id=f"lost-{label.lower()}"), )
                        ],width = 2
                    ) for label in labels]
                )
            ]
        ),
            dbc.CardFooter(
                html.Div(
                    [
                        dbc.Button('Report', id='reason-report', className='me-2'),
                        dbc.Button('Fixed',id='fixed-btn', disabled=True),
                    ],className='mt-3 right-aligned-buttons',
            )
        )
    ])

reason_form = html.Div(reason_form2,id='reason-form', style={'display': 'none'}, className='mb-5 form-container')
# label and input for the form (Weather, Icing, Power, Observer, Other)


form_choice = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.RadioItems(id='form-choice',
                                   options=[{'label': 'Create New', 'value': 'new'},
                                            {'label': 'Edit Existing', 'value': 'edit'}],
                inline=True,
                value='new',
                labelStyle={'display': 'block', 'marginRight': '20px'},
                style={'marginBottom': '20px'}  # Style for the RadioItems
            ),width=8),
                dbc.Col(
                    dbc.Button(html.Span(['Next ', html.Span('\u27A1', style={'fontSize': '18px'})]),  # Unicode arrow
                               color='secondary',
                               id='next-button',
                               n_clicks=0),
                    width=4,  # Adjust the width as needed
                    style={'textAlign': 'right'}  # Align the button to the right
                )],
            justify='between', )],
    className='form-container',id='form-choice-container')

# Define the layout for time log
time_input = html.Div([
    dbc.Card([
        dbc.CardHeader(html.H5("Log Operation Date and Time")),
        dbc.CardBody(
            dbc.Row([
                dbc.Col(dcc.DatePickerSingle(id='date-picker'), width=4),
                dbc.Col([
                    dbc.Label('Arrival Time HH:MM'),
                    dbc.Input(id='arrival-time', type='text')
                ], className='text-center', width=4),
                dbc.Col([
                    dbc.Label('Shutdown Time HH:MM'),
                    dbc.Input(id='shutdown-time', type='text')
                ], className='text-center', width=4)
            ], justify='center', align='center', className='mb-3')
        )
    ], className='mb-5')
])


cancel_form = dbc.Form(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Label('Lost Start Time HH:MM'),
                        dbc.Input(type='text', id='lost-start-time')
                    ],
                    width='auto'
                ),
                dbc.Col(
                    [
                        dbc.Label('Lost End Time HH:MM'),
                        dbc.Input(type='text', id='lost-end-time')
                    ],
                    width='auto'
                ),
                dbc.Col(dbc.Button('Add', id='add-button',  disabled=True,n_clicks=0),width='auto'),
                dbc.Col(dbc.Button('Remove ', id='remove-button', disabled=True, n_clicks=0), width='auto'),
            ]
        )
    ]
)


cancel_input = html.Div(
    dbc.Card(
        [
            dbc.CardHeader(html.H5("Log Cancellation")),
            dbc.CardBody(
                [
                    html.Div(cancel_form),
                    html.Div(id='list-container-div',
                             style={'maxHeight': '300px', 'overflowY': 'auto', 'display': 'none'},
                             className='form-container'),
                ]

            ),

        ]
    )

)




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

form_input = html.Div(id='form-container',children=[
    html.Div([
        time_input,
        instrument_status,
        cancel_input,
    ],style={'border': '1px solid grey', 'padding': '20px', 'border-radius': '10px', 'marginBottom': '50px'}),


    dbc.Row([
        dbc.Col(dbc.Button('Save Form', id='save-button', className='large-button', color='secondary'),  width='auto'),
        dbc.Col(dbc.Button('Submit Form', id='submit-button', className='large-button', color='secondary'), width='auto')
    ],justify='end'),],style={'display': 'none'},
    )
