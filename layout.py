import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, Input, Output, State
import dash_auth

lost_reason = ['Bad Weather', 'Scheduled observer team not available',
               'Problem with the telescope (e.g. drive system, active surface, M2, M3, etc.)',
               'Site problem (e.g. power, ice on dish, etc.)', 'Other']

instruments = ['TolTEC', 'SEQUOIA']

red_star_style = {"color": "red", 'margin-right': '5px'}
# create a list of hours and minutes for the dropdown
def create_dropdown(id_prefix, label, options):
    return dbc.Row([
        dbc.Col(html.Label([
            html.Span("*", style=red_star_style),  # Red star

            # f"{label}"  # Label text
         f"{id_prefix} {label}"  # Label text

        ]), width='auto'),
        dbc.Col(dcc.Dropdown(id=f'{id_prefix}-{label.lower()}-dropdown', options=options),),
    ], justify='center', align='center', className='mb-3')

def create_time_selector(id_prefix):
    hours = [{'label': str(h).zfill(2), 'value': str(h).zfill(2)} for h in range(24)]
    minutes = [{'label': str(m).zfill(2), 'value': str(m).zfill(2)} for m in range(60)]

    hour_dropdown = create_dropdown(id_prefix, "Hour", hours)
    minute_dropdown = create_dropdown(id_prefix, "Minute", minutes)

    return html.Div([
                     # dbc.Row(dbc.Col(dbc.Label(id_prefix.capitalize(), style={'font-weight':'bold'}),
                     #                 width={'size':'auto', 'offset': 1})),
                     dbc.Row([
                         # dbc.Col(dbc.Label(id_prefix.capitalize()), width='auto'),
                         dbc.Col(hour_dropdown, width=5),
                         dbc.Col(minute_dropdown, width=5)
                     ], justify='start', align='bottom', className='g-0 mb-3')])

#Navbar

navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand("Telescope Operation Log", className="ml-3"),  # Space at the beginning
            dbc.NavbarToggler(id="navbar-toggler"),
            dbc.Collapse(
                dbc.Row(
                    [
                        dbc.Col(dbc.NavLink("Operator: admin",style={'color': 'white'}), width='auto'),
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



# Define the layout for time log
time_log = html.Div([
    dbc.Card([
        dbc.CardHeader(dbc.Row([dbc.Col(html.H5('Log for date'), width='auto'),
                                dbc.Col(dcc.DatePickerSingle(id='date-picker'))], justify='center', align='end')),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_time_selector('arrival'), className='text-center'),
                dbc.Col(create_time_selector('shutdown'), className='text-center'),
            ], justify='center',align='end' )

        ])
    ])
], className='mb-5')

# Observation cancellation or lost layout
observation_cancel = html.Div([
    dbc.Card([
        dbc.CardHeader(dbc.Checklist(options=['Observation Cancellation or Lost'], id='check-lost'), ),
        dbc.CardBody([
            dbc.Row([
                dbc.Col(create_time_selector('lost-start'), className='text-center'),
                dbc.Col(create_time_selector('lost-end'), className='text-center'),
            ], justify='center', align='end', className='mb-5'),
            dbc.Row(html.H5([html.Span("*", style=red_star_style), 'Check the reasons for Cancellation or Lost Time'])),
            dbc.Row(dbc.Checklist(id='reason-input',options=[{'label': i, 'value': i} for i in lost_reason]),
            className='mb-5'),
            html.Div([html.Span("*", style=red_star_style),'Other Reason',
                dbc.Textarea(id='other-reason')], id='note-display',style={'display': 'none'}),
        ], style={'display': 'none'}, id='observation-cancel-body')
    ])
], className='mb-5' )

instrument_status = html.Div([
        dbc.Card([
            dbc.CardHeader("Facility Instruments Status"),
            dbc.CardBody([
                dbc.Checklist(id='instrument-status',
                options = [{"label": instrument, 'value': instrument} for instrument in instruments], switch=True),
            ]

            )
        ])
    ], className='mb-5')

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