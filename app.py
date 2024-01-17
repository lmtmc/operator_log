import dash
import dash_auth
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import datetime
import re
from layout import time_log, observation_cancel, instrument_status
import functions
# Username and password for the app
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin'
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
    dbc.Row(html.H1("Telescope Operation Log", style={'textAlign':'center'}), justify='center', align="center", className='mb-5 mt-5'),
    time_log,
    observation_cancel,
    instrument_status,

    dbc.Row(dbc.Alert(id='validation-message', color='primary', dismissable=True,is_open=False), className='mb-5'),
    dbc.Row(dbc.Col(dbc.Button('Submit', id='submit-button', color='primary'), width='auto'), justify='end'),
    dbc.Row(dbc.Col(dbc.Button('Log', id='history-button', color='secondary', )), className='mb-5'),
    dbc.Row(dbc.Col(html.Div(id='table-container')),className='mb-5'),

], id='page-content', className='mt-5')

# Database connection
def db_connection():
    conn = sqlite3.connect('record.db')
    return conn

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

# if check-lost is checked, show the observation-cancel-body
@app.callback(
    Output('observation-cancel-body', 'style'),
    Input('check-lost', 'value')
)
def show_observation_cancel(value):
    if value:
        return {'display': 'block'}
    return {'display': 'none'}

# change date to current date on page refresh
@app.callback(
    Output('date-picker', 'date'),
    Input('page-content','children')
)
def change_date_dynamic(page_content):
    return datetime.datetime.today().date()

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
    Output('validation-message', 'is_open'),
    Output('validation-message', 'children'),
    Input('submit-button', 'n_clicks'),
    State('date-picker', 'date'),
    State('arrival-hour-dropdown', 'value'),
    State('arrival-minute-dropdown', 'value'),
    State('shutdown-hour-dropdown', 'value'),
    State('shutdown-minute-dropdown', 'value'),
    State('check-lost', 'value'),
    State('lost-start-hour-dropdown', 'value'),
    State('lost-start-minute-dropdown', 'value'),
    State('lost-end-hour-dropdown', 'value'),
    State('lost-end-minute-dropdown', 'value'),
    State('reason-input', 'value'),
    State('other-reason', 'value'),
    State('instrument-status', 'value'),
)
def validate_input(n_clicks, date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, is_observation_cancelled, lost_start_hour,
                   lost_start_minute, lost_end_hour, lost_end_minute, reason, other_reason, instrument):
    if not n_clicks:
        return False, ''
    # print(date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, cancel, lost_start_hour,
    #                lost_start_minute, lost_end_hour, lost_end_minute, reason, other_reason, instrument)
    if not all([date, arrival_hour, arrival_minute, shutdown_hour, shutdown_minute, instrument_status]):
        return True, 'Please fill in all the fields marked with *'

    if is_observation_cancelled:
        if not all([lost_start_hour, lost_start_minute, lost_end_hour, lost_end_minute]):
            return True, 'Cancellation is selected. Please fill in all the lost time and reason with *'

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
        reason_str = ', '.join(reason) if reason else ''
        instrument_str = ', '.join(instrument) if instrument else ''

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
    Output('table-container', 'children'),
    Input('history-button', 'n_clicks'),
)
def show_history(n_clicks):
    if not n_clicks:
        return ''

    try:
        with db_connection() as conn:
            # Check if the table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='operation_log';")
            if not cursor.fetchone():  # If the table does not exist
                return html.Div('No history data available.')

            # If the table exists, fetch data and create the table
            df = pd.read_sql('SELECT * FROM operation_log', conn)
            return dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True)

    except Exception as e:
        print(e)
        return html.Div(f'An error occurred while fetching data: {e}')


if __name__ == '__main__':
    app.run_server(debug=True)