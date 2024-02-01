import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import datetime
import re
from layout import navbar,form_choice, form_input, table_modal
import functions
import urllib.parse
from dash import no_update
# Username and password for the app
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin',
    'test': 'test'
}

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Authentication for the app
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

# Layout of the app
app.layout = dbc.Container([

    navbar,
    form_input,
    form_choice,
    form_input,
    table_modal,
    dbc.Row(dcc.ConfirmDialog(id='validation-message', displayed=False), className='mb-5'),
    dcc.Store(id='saved-data', storage_type='local'),

    dcc.Download(id='download-dataframe-csv'),


], id='page-content', className='mt-5')

form_data_output = [
    Output('date-picker', 'date', allow_duplicate=True),
    Output('arrival-hour-dropdown', 'value',allow_duplicate=True),
    Output('arrival-minute-dropdown', 'value',allow_duplicate=True),
    Output('shutdown-hour-dropdown', 'value',allow_duplicate=True),
    Output('shutdown-minute-dropdown', 'value',allow_duplicate=True),
    Output('lost-start-hour-dropdown', 'value',allow_duplicate=True),
    Output('lost-start-minute-dropdown', 'value',allow_duplicate=True),
    Output('lost-end-hour-dropdown', 'value',allow_duplicate=True),
    Output('lost-end-minute-dropdown', 'value',allow_duplicate=True),
    Output('reason-input', 'value',allow_duplicate=True),
    Output('other-reason', 'value',allow_duplicate=True),
    Output('instrument-status', 'value',allow_duplicate=True),
]
# Database connection
def db_connection():
    conn = sqlite3.connect('record.db')
    return conn

# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    return not is_open if n else is_open

# if next button is clicked, show the form input
@app.callback(
    [
        Output('form-container', 'style', allow_duplicate=True),
        Output('form-choice-container', 'style'),
        *form_data_output
    ],
    Input('next-button', 'n_clicks'),
    Input('saved-data', 'data'),
    State('form-choice', 'value'),
    prevent_initial_call=True
)
def show_form(n_clicks, saved_data, choice):
    if n_clicks is None or n_clicks == 0:
        return no_update

    if choice == 'new':

        return {'display': 'block'}, {'display': 'none'}, datetime.datetime.today().date(),None,None,None,None,None,None,None,None,[None],None,[None]
    elif choice == 'edit':
        print('retrieve data',saved_data)
        if saved_data:

            return {'display': 'block'},  {'display': 'none'},saved_data['date'],saved_data['arrival_hour'],saved_data['arrival_minute'],saved_data['shutdown_hour'],saved_data['shutdown_minute'],saved_data['lost_start_hour'],saved_data['lost_start_minute'],saved_data['lost_end_hour'],saved_data['lost_end_minute'],saved_data['reason'],saved_data['other_reason'],saved_data['instrument']
        else:
            return {'display': 'none'}, {'display': 'none'},no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update,no_update
    return no_update

# if save button is clicked, save the data to dcc.store
@app.callback(
    Output('saved-data', 'data'),
    Input('save-button', 'n_clicks'),
    State('date-picker', 'date'),
    State('arrival-hour-dropdown', 'value'),
    State('arrival-minute-dropdown', 'value'),
    State('shutdown-hour-dropdown', 'value'),
    State('shutdown-minute-dropdown', 'value'),
    State('lost-start-hour-dropdown', 'value'),
    State('lost-start-minute-dropdown', 'value'),
    State('lost-end-hour-dropdown', 'value'),
    State('lost-end-minute-dropdown', 'value'),
    State('reason-input', 'value'),
    State('other-reason', 'value'),
    State('instrument-status', 'value'),
    prevent_initial_call=True
)
def save_data(n_clicks, date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, lost_start_hour,
                lost_start_minute, lost_end_hour, lost_end_minute, reason, other_reason, instrument):
        if not n_clicks:
            return no_update

        if ctx.triggered[0]['prop_id'].split('.')[0] == 'save-button':
            print(date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, lost_start_hour,
                           lost_start_minute, lost_end_hour, lost_end_minute, reason, other_reason, instrument)
            return {'date': date, 'arrival_hour': arrival_hour, 'arrival_minute': arrival_minute,
                'shutdown_hour': shutdown_hour, 'shutdown_minute': shutdown_minute,
                'lost_start_hour': lost_start_hour, 'lost_start_minute': lost_start_minute,
                'lost_end_hour': lost_end_hour, 'lost_end_minute': lost_end_minute,
                'reason': reason, 'other_reason': other_reason, 'instrument': instrument}
        return no_update

# Callback to update shutdown hour and minute dropdown based on arrival time
@app.callback(
    Output('shutdown-hour-dropdown', 'options'),
    Output('shutdown-minute-dropdown', 'options'),
    Input('arrival-hour-dropdown', 'value'),
    Input('arrival-minute-dropdown', 'value'),
    Input('shutdown-hour-dropdown', 'value'),
)
def update_shutdown_time(hour, minute, shutdown_hour):
    return functions.update_end_time_dropdown(hour, minute, shutdown_hour)

# Callback to update lost end hour and minute dropdown based on lost start time
@app.callback(
    Output('lost-end-hour-dropdown', 'options'),
    Output('lost-end-minute-dropdown', 'options'),
    Input('lost-start-hour-dropdown', 'value'),
    Input('lost-start-minute-dropdown', 'value'),
    Input('lost-end-hour-dropdown', 'value'),
)
def update_lost_end_time(hour, minute, lost_end_hour):
    return functions.update_end_time_dropdown(hour, minute, lost_end_hour)


# if other option is selected in the checklist, show the other reason input
@app.callback(
    Output('note-display', 'style'),
    Input('reason-input', 'value'),
)
def show_other_reason(value):
    if value and 'Other' in value:
        return {'display': 'block'}
    return {'display': 'none'}

# if submit button is clicked, check if all the filled are filled
@app.callback(
    Output('validation-message', 'displayed'),
    Output('validation-message', 'message'),
    Input('submit-button', 'n_clicks'),
    State('date-picker', 'date'),
    State('arrival-hour-dropdown', 'value'),
    State('arrival-minute-dropdown', 'value'),
    State('shutdown-hour-dropdown', 'value'),
    State('shutdown-minute-dropdown', 'value'),
    State('lost-start-hour-dropdown', 'value'),
    State('lost-start-minute-dropdown', 'value'),
    State('lost-end-hour-dropdown', 'value'),
    State('lost-end-minute-dropdown', 'value'),
    State('reason-input', 'value'),
    State('other-reason', 'value'),
    State('instrument-status', 'value'),
)
def validate_input(n_clicks, date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, lost_start_hour,
                   lost_start_minute, lost_end_hour, lost_end_minute, reason, other_reason, instrument_status):
    if not n_clicks:
        return False, ''
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'submit-button':
        # print(date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, lost_start_hour,
        #                lost_start_minute, lost_end_hour, lost_end_minute, reason, other_reason, instrument_status)
        if not all([date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, instrument_status]):
            return True, 'Please fill in all the fields marked with *'

        if reason and 'Other' in reason and not other_reason:
            return True, 'You selected "Other" as a reason. Please provide the additional information.'
        # if all fields are filled, proceed to save the data to the database
        try:
            conn = db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS operation_log (
                    date TEXT,
                    arrival_time TEXT,
                    shutdown_time TEXT,
                    lost_start_time TEXT,
                    lost_end_time TEXT,
                    reason TEXT,
                    other_reason TEXT,
                    instrument_status TEXT
                )
            ''')

            # Handle None values for lost_start_time and lost_end_time
            lost_start_time = f'{lost_start_hour}:{lost_start_minute}' if lost_start_hour and lost_start_minute else ''
            lost_end_time = f'{lost_end_hour}:{lost_end_minute}' if lost_end_hour and lost_end_minute else ''

            # Convert reason and instrument lists to strings
            reason_str = ', '.join(filter(None,reason)) if reason else ''
            instrument_str = ', '.join(filter(None,instrument_status)) if instrument_status else ''

            cursor.execute('INSERT INTO operation_log (date, arrival_time, shutdown_time, lost_start_time, lost_end_time, reason, other_reason, instrument_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (date, f'{arrival_hour}:{arrival_minute}', f'{shutdown_hour}:{shutdown_minute}',
                            lost_start_time, lost_end_time,
                            reason_str, other_reason, instrument_str)
                           )
            conn.commit()
            conn.close()
        except Exception as e:
            print(e)
            return True, f'An error occurred while saving the data: {e}'
        return True, 'All fields are filled and data has been saved successfully'

# if history button is clicked, show the history table
@app.callback(
    Output('table-container', 'is_open'),
    Output("modal-body-content", 'children'),
    Input('history-button', 'n_clicks'),
    Input('close-modal', 'n_clicks'),
    State('table-container', 'is_open'),
    prevent_initial_call=True
)
def show_history(n1, n2, is_open):
    if not ctx.triggered:
        return no_update, no_update
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if button_id == 'history-button':
        try:
            with db_connection() as conn:
                # Check if the table exists
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operation_log';")
                if not cursor.fetchone():  # If the table does not exist
                    return html.Div('No history data available.')

                # If the table exists, fetch data and create the table
                df = pd.read_sql('SELECT * FROM operation_log', conn)
                return not is_open, dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

        except Exception as e:
            print(e)
            return is_open, no_update
    elif button_id == 'close-modal':
        return not is_open, no_update
    return no_update, no_update

# if download button is clicked, download the data as csv
@app.callback(
    Output('download-dataframe-csv', 'data'),
    Input('download-button', 'n_clicks'),
    prevent_initial_call=True
)
def download_data(n_clicks):
    if not n_clicks:
        raise PreventUpdate

    try:
        with db_connection() as conn:
            # Check if the table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operation_log';")
            if not cursor.fetchone():  # If the table does not exist
                return PreventUpdate

            # If the table exists, fetch data and create the table
            df = pd.read_sql('SELECT * FROM operation_log', conn)
            df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
            # csv_string = df.to_csv(index=False, encoding='utf-8')
            # csv_string = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_string)
            return dcc.send_data_frame(df.to_csv, "operation_log.csv", index=False)

    except Exception as e:
        print(e)
        return PreventUpdate
if __name__ == '__main__':
    app.run_server(debug=True)