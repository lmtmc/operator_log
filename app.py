import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update, dash_table
from dash.exceptions import PreventUpdate
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from layout import (navbar,operator_arrive, shutdown_time, instrument_status,problem_form,restart_form,
                    ObsNum_form, log_history)
from db import add_log_entry, fetch_log_data,init_db, current_time, current_time_input, log_time

# Initialize the database if it fails to initialize then run python3 db.py first
init_db()

Valid_Username_Password_Pairs = {
    'lmtmc': 'hello'
}

prefix = '/operator_log/'
# Initialize the Dash app
app = dash.Dash(__name__, requests_pathname_prefix = prefix, routes_pathname_prefix=prefix, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True)
# auth = dash_auth.BasicAuth(app, Valid_Username_Password_Pairs)


data_column = ['ID', 'Timestamp', 'Operator Name', 'Arrival Time', 'Shutdown Time', 'RSR', 'SEQUOIA', 'TolTEC', '1mm',
                 'ObsNum', 'Keyword', 'Entry', 'Lost Time', 'Restart Time', 'Lost Time Weather', 'Lost Time Icing', 'Lost Time Power',
                 'Lost Time Observers', 'Lost Time Other']

# Layout of the app
app.layout = dbc.Container([

    navbar,
    dbc.Container([
        dbc.Row([
            dbc.Col([operator_arrive, instrument_status, ObsNum_form], ),
            dbc.Col([problem_form, restart_form, shutdown_time]),]),
        html.Div(log_history),
        dcc.Download(id='download-log')
    ]),
])

server = app.server
instruments = ['rsr', 'sequoia', 'toltec', '1mm']

@app.callback(
        Output('log-table', 'rowData'),

    [
        Input('arrival-btn', 'n_clicks'),#0
        Input('instrument-btn', 'n_clicks'),#1
        Input('entry-btn', 'n_clicks'),#2
        Input('problem-btn', 'n_clicks'),#3
        Input('restart-btn', 'n_clicks'),#4
        Input('shutdown-btn', 'n_clicks'),#5
    ],
    [
        State('operator-name-input', 'value'),#6
        State('arrival-time-input', 'value'),#7
        State('restart-time-input', 'value'),#8
        State('shutdown-time-input', 'value'),#9
    ] + [
        State(instrument, 'value') for instrument in instruments #10-13
    ] + [
        State('obsnum-input', 'value'), #14
        State('keyword-input', 'value'), #15
        State('keyword-checklist', 'value'),#16
        State('entry-input', 'value'),#17
    ] +
    [
        State('problem-log-time', 'value') #18
    ] + [
        State(f"lost-{label.lower()}", 'value') for label in ['Weather', 'Icing', 'Power', 'Observers', 'Other']
    ], #19-23
    prevent_initial_call=True
)
def update_log(*args):
    if ctx.triggered_id is None:
        raise PreventUpdate
    timestamp = current_time()
    operator_name = args[6]
    if ctx.triggered_id == 'arrival-btn':
        arrival_time = log_time(args[7])
        add_log_entry(timestamp=timestamp, operator_name=operator_name, arrival_time=arrival_time)
    if ctx.triggered_id == 'instrument-btn':
        instrument_statuses = {instruments[i]: 1 if args[i+10] is not None and args[i+10][0] == 1 else 0 for i in range(4)}
        add_log_entry(timestamp=timestamp, operator_name=operator_name, rsr=instrument_statuses['rsr'], sequoia=instrument_statuses['sequoia'], toltec=instrument_statuses['toltec'], one_mm=instrument_statuses['1mm'])
    if ctx.triggered_id == 'entry-btn':
        obsNum, keyword, keyword_checklist, entry = args[14], args[15], args[16], args[17]
        keyword_checklist = ', '.join(keyword_checklist) if keyword_checklist else ''
        if keyword == 'None':
            keyword = ''
        keywords = keyword + ', ' + keyword_checklist if keyword else keyword_checklist
        add_log_entry(timestamp=timestamp, operator_name=operator_name, obsNum=obsNum, keywords=keywords, entry=entry)
    if ctx.triggered_id == 'problem-btn':
        lost_time = log_time(args[18])
        lost_time_details = {f'lost_time_{label.lower()}': args[i+19] for i, label in enumerate(['Weather', 'Icing', 'Power', 'Observers', 'Other'])}
        add_log_entry(timestamp=timestamp, operator_name=operator_name, lost_time=lost_time, **lost_time_details)
    if ctx.triggered_id == 'restart-btn':
        restart_time = log_time(args[8])
        add_log_entry(timestamp=timestamp, operator_name=operator_name, restart_time=restart_time)
    if ctx.triggered_id == 'shutdown-btn':
        shutdown_time = log_time(args[9])
        add_log_entry(timestamp=timestamp, operator_name=operator_name, shutdown_time=shutdown_time)
    return fetch_log_data(10)

# if the arrive-now button is clicked, save the current time in the arrival time input
# if the problem-now button is clicked, save the current time in the problem time input
# if the shutdown-now button is clicked, save the current time in the shutdown time input
# if the restart-now button is clicked, save the current time in the restart time input
@app.callback(
    Output('arrival-time-input', 'value', allow_duplicate=True),
    Output('problem-log-time', 'value', allow_duplicate=True),
    Output('shutdown-time-input', 'value', allow_duplicate=True),
    Output('restart-time-input', 'value', allow_duplicate=True),
    Input('arrive-now-btn', 'n_clicks'),
    Input('problem-log-now-btn', 'n_clicks'),
    Input('showdown-now-btn', 'n_clicks'),
    Input('restart-now-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_now_click(arrive_clicks, problem_clicks, shutdown_clicks, restart_clicks):
    if ctx.triggered_id is None:
        raise PreventUpdate
    if ctx.triggered_id == 'arrive-now-btn':
        return current_time_input(), no_update, no_update, no_update
    if ctx.triggered_id == 'problem-log-now-btn':
        return no_update, current_time_input(), no_update, no_update
    if ctx.triggered_id == 'showdown-now-btn':
        return no_update, no_update, current_time_input(), no_update
    if ctx.triggered_id == 'restart-now-btn':
        return no_update, no_update, no_update, current_time_input()

# clear Arrival input filed when save button is clicked
@app.callback(
    Output('arrival-time-input', 'value'),
    Input('arrival-btn', 'n_clicks'),
    prevent_initial_call=True)
def clear_input(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return current_time_input()

# clear operator name input when click the clear button
@app.callback(
    Output('operator-name-input', 'value'),
    Input('clear-name-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_input(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return ''
# clear ObsNum input filed when save button is clicked
@app.callback(
    [
        Output('obsnum-input', 'value'),
        Output('keyword-input', 'value'),
        Output('keyword-checklist', 'value'),
        Output('entry-input', 'value'),
    ],
    Input('entry-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_input(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return '', '', '', ''

# clear Problem input filed when save button is clicked
@app.callback(
    [
        Output('problem-log-time', 'value'),
        Output('lost-weather', 'value'),
        Output('lost-icing', 'value'),
        Output('lost-power', 'value'),
        Output('lost-observers', 'value'),
        Output('lost-other', 'value'),
    ],
    Input('problem-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_input(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return current_time_input(), '', '', '', '', ''

# clear Restart input filed when save button is clicked
@app.callback(
    Output('restart-time-input', 'value'),
    Input('restart-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_input(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return current_time_input()

# clear Shutdown input filed when save button is clicked
@app.callback(
    Output('shutdown-time-input', 'value'),
    Input('shutdown-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_input(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return current_time_input()

# click the download log button, download the log db as a csv file
@app.callback(
    Output('download-log', 'data'),
    Input('download-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_download_log_click(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    log_data = fetch_log_data(None)
    log_df = pd.DataFrame(log_data, columns=data_column)
    return dcc.send_data_frame(log_df.to_csv, 'log.csv', index=False)

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_props_check=False, threaded=False)
