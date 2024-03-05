import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update, dash_table
from dash.exceptions import PreventUpdate
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from layout import (login_page, dash_app_page, navbar)
from db import add_log_entry, fetch_log_data,init_db, current_time, current_time_input, log_time

import flask
from flask import redirect, url_for, render_template_string, request
import os
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
server = flask.Flask(__name__)
server.secret_key = os.urandom(24)
# Initialize the database if it fails to initialize then run python3 db.py first
init_db()

Valid_Username_Password_Pairs = {
    'lmtmc': 'hello', 'lmtmc1': 'hello', 'lmtmc2': 'hello'
}

prefix = '/operator_log/'

# Initialize the Dash app
app = dash.Dash(__name__, requests_pathname_prefix = prefix, routes_pathname_prefix=prefix,
                server = server, title='LMT Operator Log',
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True)
# auth = dash_auth.BasicAuth(app, Valid_Username_Password_Pairs)

# Login manager object will be used to log in/logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_prefix = prefix.lstrip('/') # remove the leading character from the prefix
login_manager.login_view = f'{login_prefix}login'

# User class for flask-login
class User(UserMixin):
    def __init__(self, username):
        self.id = username
@login_manager.user_loader
def load_user(username):
    return User(username)

data_column = ['ID', 'Timestamp', 'Operator Name', 'Arrival Time', 'Shutdown Time', 'RSR', 'SEQUOIA', 'TolTEC', '1mm',
                 'ObsNum', 'Keyword', 'Entry', 'Lost Time', 'Restart Time', 'Lost Time Weather', 'Lost Time Icing', 'Lost Time Power',
                 'Lost Time Observers', 'Lost Time Other']

# Layout of the app



app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content'),
])

instruments = ['rsr', 'sequoia', 'toltec', '1mm']

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def display_page(pathname):
    if not current_user.is_authenticated:
        return login_page
    else:
        return dash_app_page

# callback for the login button
@app.callback(Output('url', 'pathname', allow_duplicate=True),
              [Input('login-btn', 'n_clicks')],
              [State('username', 'value'), State('password', 'value')],
              prevent_initial_call=True)
def login(n_clicks, username, password):
    if username in Valid_Username_Password_Pairs and Valid_Username_Password_Pairs[username] == password:
        user = User(username)
        login_user(user)
        return prefix  # Redirect to the home/dashboard page
    return no_update  # Stay on the login page if incorrect credentials

@app.callback(Output('url', 'pathname'), [Input('logout-btn', 'n_clicks')],
              prevent_initial_call=True)
def logout(n_clicks):
    if n_clicks > 0:
        logout_user()
        return f'{prefix}login'  # Redirect to login page after logout
    return no_update

# update login name and logout in the navbar
@app.callback(Output('login-name', 'children'),
              Output('logout-btn', 'children'),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def update_login_name(pathname):
    if current_user.is_authenticated:
        return f"Login As: {current_user.id}", "Logout"
    return '', ''

# update the operator name when the tab is opened
@app.callback(Output('operator-name-input', 'value', allow_duplicate=True),
              Input('tabs', 'active_tab'),
              )
def update_operator_name(active_tab):
    if active_tab and current_user.is_authenticated:
        return current_user.id
    return ''
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
    app.run_server(debug=True, dev_tools_props_check=False, threaded=False)
