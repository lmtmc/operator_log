import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import datetime
from layout import navbar,form_choice, form_input, table_modal

# Username and password for the app
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'admin',
    'test': 'test'
}
lost_reason = ['Bad Weather', 'Scheduled observer team not available',
               'Problem with the telescope (e.g. drive system, active surface, M2, M3, etc.)',
               'Site problem (e.g. power, ice on dish, etc.)', 'Other']
# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'])

# Authentication for the app
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)



# Layout of the app
app.layout = dbc.Container([

    navbar,
    form_choice,
    form_input,
    table_modal,
    dbc.Row(dcc.ConfirmDialog(id='validation-message', displayed=False), className='mb-5'),
    dcc.Store(id='saved-data', storage_type='local'),

    dcc.Download(id='download-dataframe-csv'),


], id='page-content', className='mt-5')
instruments = ['TolTEC', 'SEQUOIA', 'RSR', '1mm Rx']

form_data_output = [
    Output('date-picker', 'date', allow_duplicate=True),
    Output('arrival-time', 'value',allow_duplicate=True),
    Output('shutdown-time', 'value',allow_duplicate=True),
    Output(instruments[0], 'value',allow_duplicate=True),
    Output(instruments[1], 'value',allow_duplicate=True),
    Output(instruments[2], 'value',allow_duplicate=True),
    Output(instruments[3], 'value',allow_duplicate=True),
    Output('list-container-div', 'children',allow_duplicate=True),
]

clear_form = [datetime.datetime.today().date(),'','',False,False,False,False,'']
# Database connection
def db_connection():
    conn = sqlite3.connect('record.db')
    return conn

# if next button is clicked, show the form input, hide the form choice
@app.callback(
    [
        Output('form-container', 'style', allow_duplicate=True),
        Output('form-choice-container', 'style'),
        *form_data_output
    ],
    [
        Input('next-button', 'n_clicks')
    ],
    [
        State('saved-data', 'data'),
        State('form-choice', 'value')
    ],
    prevent_initial_call=True
)
def show_form(n_clicks, saved_data, choice):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    if choice == 'new':
        return [{'display': 'block'}, {'display': 'none'}] + clear_form
    elif choice == 'edit':
        if saved_data:
            data_values = list(saved_data.values())
            return {'display': 'block'},  {'display': 'none'}, *data_values
        else:

            return {'display': 'none'}, {'display': 'none'},no_update,no_update,no_update,no_update,no_update
    return PreventUpdate

# if lost start time, lost end time, or reason input are filled, then the add cancellation button is enabled
@app.callback(
    Output('add-button', 'disabled'),
    Input('lost-start-time', 'value'),
    Input('lost-end-time', 'value'),
    Input('reason-input', 'value'),
    prevent_initial_call=True
)
def enable_add_button(lost_start, lost_end, reason):
    if reason:
        reason = reason[0] if len(reason) == 1 else reason
    if lost_start and lost_end and reason:
        return False
    return True

# if the items in the list-container-div is selected remove button is enabled
@app.callback(
    Output('remove-button', 'disabled'),
    Input({'type': 'done', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def enable_remove_button(values):

    value = [val for val in values if val]
    if value:
        return False
    return True

# If add button is clicked, add the new item to the list
@app.callback(
    Output('list-container-div', 'children', allow_duplicate=True),
    Output('list-container-div', 'style', allow_duplicate=True),
    Output('lost-start-time', 'value', allow_duplicate=True),
    Output('lost-end-time', 'value', allow_duplicate=True),
    Output('reason-input', 'value', allow_duplicate=True),
    Input('add-button', 'n_clicks'),
    State('lost-start-time', 'value'),
    State('lost-end-time', 'value'),
    State('reason-input', 'value'),
    State('other-reason', 'value'),
    prevent_initial_call=True,
)
def add_item(n_clicks, start_time, end_time, reason, other_reason):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    # concatenate the reasons
    patched_list = Patch()
    if reason and 'Other' in reason:
        if other_reason:
            reason = [other_reason if item=='Other' else item for item in reason]
    reason = ', '.join(item for item in reason if item is not None)
    new_item = html.Div(
        [
            dcc.Checklist(
                options=[{'label': "", "value":"done"}],
                id={"index": n_clicks, "type": "done"},
                style={"display":"inline"},
                labelStyle={"display":"inline"},
            ),
            html.Div(
                [f'Cancel from {start_time} to {end_time} due to {reason}'],
                id={"index": n_clicks, "type": "output-str"},
                style={"display":"inline", "margin":"10px"},
            )
        ]
    )
    # append the new item to the list
    patched_list.append(new_item)
    return patched_list, {'display':'block'}, '', '', ''

# callback to remove the selected item from the list
@app.callback(
    Output('list-container-div', 'children', allow_duplicate=True),
    Input('remove-button', 'n_clicks'),
    State({'index':ALL, 'type':"done"},"value"),
    prevent_initial_call=True,
)
def remove_item(n_clicks, values,):
    patched_list = Patch()
    values_to_remove = []
    for i, val in enumerate(values):
        if val:
            values_to_remove.insert(0,i)
        for v in values_to_remove:
            del patched_list[v]
    return patched_list


# if save button is clicked, save log date, arrival time, shutdown time, instruments, cancellation  to dcc.store


@app.callback(
    Output('saved-data', 'data'),
    Input('save-button', 'n_clicks'),
    State('date-picker', 'date'),
    State('arrival-time', 'value'),
    State('shutdown-time', 'value'),
    State('TolTEC', 'value'),
    State('SEQUOIA', 'value'),
    State('RSR', 'value'),
    State('1mm Rx', 'value'),
    State('list-container-div', 'children'),
    prevent_initial_call=True
)
def save_data(n_clicks, date, arrival_time, shutdown_time, instrument0,instrument1, instrument2, instrument3, children):
     if n_clicks is None or n_clicks == 0:
          raise PreventUpdate
     if ctx.triggered[0]['prop_id'].split('.')[0] == 'save-button':
          return {'date-picker': date, 'arrival-time': arrival_time, 'shutdown-time': shutdown_time,
                  instruments[0]: instrument0, instruments[1]: instrument1, instruments[2]: instrument2,
                  instruments[3]: instrument3, 'cancel-info': children}
     return no_update


#
# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    return not is_open if n else is_open



# if other option is selected in the checklist, show the other reason input
@app.callback(
    Output('note-display', 'style'),
    Input('reason-input', 'value'),
)
def show_other_reason(value):
    if value and 'Other' in value:
        return {'display': 'block'}
    return {'display': 'none'}

# if log for date, arrival time and shutdown time are filled, enable the submit button
@app.callback(
    Output('submit-button', 'disabled'),
    Input('date-picker', 'date'),
    Input('arrival-time', 'value'),
    Input('shutdown-time', 'value'),
    prevent_initial_call=True
)
def enable_submit_button(date, arrival_time, shutdown_time):
    if date and arrival_time and shutdown_time:
        return False
    return True

# if submit button is clicked, check if arrival time is before shutdown time and save the data to the database

@app.callback(
    [
        Output('validation-message', 'displayed'),
        Output('validation-message', 'message'),
        form_data_output
    ],
    [
        Input('submit-button', 'n_clicks'),
    ],
    State('date-picker', 'date'),
    State('arrival-time', 'value'),
    State('shutdown-time', 'value'),
    [State(instrument, 'value') for instrument in instruments],
    State('list-container-div', 'children'),
    prevent_initial_call=True
)
def validate_input(n_clicks, date, arrival_time, shutdown_time, *args):
    instrument_status = args[:-1]
    children = args[-1]
    if not n_clicks:
        raise PreventUpdate

    if callback_context.triggered[0]['prop_id'].split('.')[0] == 'submit-button':
        if arrival_time > shutdown_time:
            return True, 'Arrival time cannot be after shutdown time', no_update, no_update, no_update, no_update, no_update, no_update, no_update

        cancel_info = []
        for child in children:
            try:
                cancel_text = child['props']['children'][1]['props']['children'][0]
                cancel_info.append(cancel_text)
            except (IndexError, KeyError):
                print("Error in parsing children")
                continue

        cancel_info_str = json.dumps(cancel_info).strip('[]')

        instrument_values_text = ['Ready' if value else 'Not Ready' for value in instrument_status]

        try:
            with db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''CREATE TABLE IF NOT EXISTS operation_log (
                                    date TEXT,
                                    arrival_time TEXT,
                                    shutdown_time TEXT,
                                    cancel_info TEXT,
                                    TolTEC TEXT,
                                    SEQUOIA TEXT,
                                    RSR TEXT,
                                    "1mm Rx" TEXT)''')   # Fixed the syntax error
                cursor.execute('INSERT INTO operation_log (date, arrival_time, shutdown_time, cancel_info, TolTEC, SEQUOIA, RSR, "1mm Rx")'
                               'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                               (date, arrival_time, shutdown_time, cancel_info_str, *instrument_values_text))
                conn.commit()
                print('Data saved successfully')
                return True, 'Data saved successfully', clear_form
        except Exception as e:
            print(e)
            return True, f'An error occurred while saving the data: {e}', no_update

    return no_update






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
            return dcc.send_data_frame(df.to_csv, "operation_log.csv", index=False)

    except Exception as e:
        print(e)
        return PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)