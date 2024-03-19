#todo revise the log table and save the observers names
import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update, dash_table
from dash.exceptions import PreventUpdate
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import time
from layout import (login_tab, dash_app_page, setting_page,navbar, prefix, admin_page)
from db import (exist_user, exist_email,delete_user,validate_user, add_user, update_user_password,fetch_user_by_username,
                fetch_all_users,add_log_entry, fetch_log_data,init_db,create_admin_user,
                current_time, current_time_input, log_time)
import flask
from flask import redirect, url_for, render_template_string, request
import os
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user, AnonymousUserMixin
server = flask.Flask(__name__)
server.secret_key = os.urandom(24)
# Initialize the database if it fails to initialize then run python3 db.py first
init_db()
create_admin_user()
# Set the prefix for the dash app
dash_prefix = f'/{prefix}/'

# Initialize the Dash app
app = dash.Dash(__name__, requests_pathname_prefix = dash_prefix, routes_pathname_prefix=dash_prefix,
                server = server, title='LMT Operator Log',
                external_stylesheets=[dbc.themes.BOOTSTRAP, "https://use.fontawesome.com/releases/v5.8.1/css/all.css"],
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True)

# Login manager object will be used to log in/logout users
login_manager = LoginManager()
login_manager.init_app(server)
login_prefix = f'{prefix}/' # remove the leading character from the prefix


# User class for flask-login
class Anonymous(AnonymousUserMixin):
    def __init__(self, is_admin=False):
        self.is_admin = is_admin
login_manager.anonymous_user = Anonymous
login_manager.login_view = f'{login_prefix}login'

# User class for flask-login
class User(UserMixin):
    def __init__(self, username, is_admin):
        self.id = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(username):
    user = fetch_user_by_username(username)
    if user:
        return User(username=user.username, is_admin=user.is_admin)
    return None

data_column = ['ID', 'Timestamp', 'Operator Name', 'Arrival Time', 'Shutdown Time', 'RSR', 'SEQUOIA', 'TolTEC', '1mm',
                 'ObsNum', 'Keyword', 'Entry', 'Lost Time', 'Restart Time', 'Lost Time Weather', 'Lost Time Icing', 'Lost Time Power',
                 'Lost Time Observers', 'Lost Time Other']

# Layout of the app



app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    dcc.Store(id='auth-store', storage_type='memory', data={'authenticated': False, 'admin': False}),
    navbar,
    html.Div(id='page-content'),
])

instruments = ['rsr', 'sequoia', 'toltec', '1mm']

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def display_page(pathname):
    if pathname.endswith(f'{prefix}/admin'):
        if current_user.is_authenticated and current_user.is_admin:
            return admin_page
        else:
            return "action denied"
    if pathname.endswith(f'/{prefix}/logout'):
        logout_user()
        return login_tab
    elif pathname.endswith(f'/{prefix}/settings'):
        if current_user.is_authenticated:
            return setting_page
        else:
            return login_tab
    elif current_user.is_authenticated:
        print('The user is normal user',current_user.is_admin)
        return dash_app_page
    return login_tab


# callback for the login button
@app.callback(Output('url', 'pathname', allow_duplicate=True),
              Output('login-status','is_open'),
              Output('login-status', 'children'),
              Output('username', 'value'),
              Output('password', 'value'),
              [Input('login-btn', 'n_clicks')],
              [State('username', 'value'), State('password', 'value')],
              prevent_initial_call=True)
def login(n_clicks, username, password):
    if username is None or password is None:
        return no_update

    if validate_user(username, password):
        data = fetch_user_by_username(username)
        user = User(username=username, is_admin=data.is_admin)
        login_user(user)
        if user.is_admin:
            return f'/{prefix}/admin', True, 'Admin Login','',''
        else:
            return f'/{prefix}/', True, 'Normal User Login','',''
    else:
        return no_update, True, 'Invalid credentials','',''
    return no_update  # Stay on the login page if incorrect credentials
# if login is successful, display username in navbar
@app.callback(Output('user-dropdown', 'label'),
                Input('url', 'pathname'),
                prevent_initial_call=True)
def display_username(pathname):
    if current_user.is_authenticated:
        return current_user.id
    return ''

# reset password
@app.callback(Output('url', 'pathname', allow_duplicate=True),
                Output('reset-status','is_open'),
                Output('reset-status', 'children'),
                Input('reset-btn', 'n_clicks'),
                State('reset-password', 'value'),
                State('reset-confirm-password', 'value'),
                prevent_initial_call=True)
def reset_password(n_clicks, password, confirm_password):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    if not password or not confirm_password:
        return no_update, True, 'Please fill in all the fields'
    if password != confirm_password:
        return no_update, True, 'Passwords do not match'
    if password and confirm_password:
        update_user_password(username = current_user.id, password=password)
        return f'/{prefix}/', True, 'Password reset successfully'
    return f'/{prefix}/reset', True, 'Error occurred'

# callback for the logout button
@app.callback(Output('url', 'pathname', allow_duplicate=True),
                [Input('logout-btn', 'n_clicks')],
                prevent_initial_call=True)
def logout(n_clicks):
    logout_user()
    return f'/{prefix}/'

# callback for the register button
@app.callback(Output('url', 'pathname', allow_duplicate=True),
              Output('register-status','is_open'),
              Output('register-status', 'children'),
              Input('register-btn', 'n_clicks'),
              State('register-username', 'value'),
              State('register-email', 'value'),
              State('register-password', 'value'),
              State('register-confirm-password', 'value'),
              prevent_initial_call=True)
def register(n_clicks, username, email, password, confirm_password):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    if not username or not email or not password or not confirm_password:
        return no_update, True, 'Please fill in all the fields'
    if exist_user(username):
        return no_update, True, 'User already exists'
    if exist_email(email):
        return no_update, True, 'Email already exists'
    if password != confirm_password:
        return no_update, True, 'Passwords do not match'
    if username and email and password and confirm_password:

        add_user(username = username, email=email, password=password, is_admin=False, create_at=current_time())
        login_user(User(username, False))
        return f'/{prefix}/', True, 'User registered successfully'
    return f'/{prefix}/register', True, 'Error occurred'

# callback for the settings button
@app.callback(Output('url', 'pathname', allow_duplicate=True),
                [Input('settings-btn', 'n_clicks')],
                prevent_initial_call=True)
def settings(n_clicks):
    return f'/{prefix}/settings' if n_clicks > 0 else no_update

# callback for back button
@app.callback(Output('url', 'pathname', allow_duplicate=True),
                [Input('back-btn', 'n_clicks')],
                prevent_initial_call=True)
def back(n_clicks):
    return f'/{prefix}/' if n_clicks > 0 else no_update

# if authenticated, show navbar, if not, hide it
@app.callback(Output('navbar', 'style'),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def show_navbar(pathname):
    if current_user.is_authenticated:
        return {}
    return {'display': 'none'}

# update the operator name when the tab is opened
@app.callback(Output('operator-name-input', 'value', allow_duplicate=True),
              Input('tabs', 'active_tab'),
              )
def update_operator_name(active_tab):
    if active_tab and current_user.is_authenticated:
        return current_user.id
    return ''

# update the log table when the tab is opened
@app.callback(Output('log-table', 'rowData', allow_duplicate=True),
              Output('log-table-div', 'style'),
              Input('view-btn', 'n_clicks'),
                prevent_initial_call=True)
def update_log_table(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return fetch_log_data(10), {'display': 'block'}

# update options for observer checklist when the tab is opened
@app.callback(Output('observers-checklist', 'options', allow_duplicate=True),
              Input('tabs', 'active_tab'),
            prevent_initial_call=True)
def update_observers_checklist(active_tab):
    if active_tab =='tab-observers':
        users = fetch_all_users()
        # exclude the admin and current user from the observer checklist
        return [{'label': user['Username'], 'value': user['Username']}
                for user in users if user['Username'] != current_user.id and not user['Is Admin']]
    return []
@app.callback(
        Output('log-table', 'rowData'),

    [
        Input('arrival-btn', 'n_clicks'),#0
        Input('instrument-btn', 'n_clicks'),#1
        Input('entry-btn', 'n_clicks'),#2
        Input('problem-btn', 'n_clicks'),#3
        Input('restart-btn', 'n_clicks'),#4
        Input('shutdown-btn', 'n_clicks'),#5
        Input('observer-btn', 'n_clicks'),#6
    ],
    [
        State('operator-name-input', 'value'),#7
        State('arrival-time-input', 'value'),#8
        State('restart-time-input', 'value'),#9
        State('shutdown-time-input', 'value'),#10
    ] + [
        State(instrument, 'value') for instrument in instruments #11-14
    ] + [
        State('obsnum-input', 'value'), #15
        State('keyword-input', 'value'), #16
        State('keyword-checklist', 'value'),#17
        State('entry-input', 'value'),#18
    ] +
    [
        State('problem-log-time', 'value') #19
    ] + [
        State(f"lost-{label.lower()}", 'value') for label in ['Weather', 'Icing', 'Power', 'Observers', 'Other']
    ] #20-24
+[
        State('observers-checklist', 'value'), #25
        State('observers-name-input', 'value') #26
    ],
    prevent_initial_call=True
)
def update_log(*args):
    if ctx.triggered_id is None:
        raise PreventUpdate
    timestamp = current_time()
    operator_name = args[7]
    if ctx.triggered_id == 'arrival-btn':
        arrival_time = log_time(args[8])
        add_log_entry(timestamp=timestamp, operator_name=operator_name, arrival_time=arrival_time)
    if ctx.triggered_id == 'instrument-btn':
        instrument_statuses = {instruments[i]: 1 if args[i+11] is not None and args[i+11][0] == 1 else 0 for i in range(4)}
        add_log_entry(timestamp=timestamp, operator_name=operator_name, rsr=instrument_statuses['rsr'], sequoia=instrument_statuses['sequoia'], toltec=instrument_statuses['toltec'], one_mm=instrument_statuses['1mm'])
    if ctx.triggered_id == 'entry-btn':
        obsNum, keyword, keyword_checklist, entry = args[15], args[16], args[17], args[18]
        keyword_checklist = ', '.join(keyword_checklist) if keyword_checklist else ''
        if keyword == 'None':
            keyword = ''
        keywords = keyword + ', ' + keyword_checklist if keyword else keyword_checklist
        add_log_entry(timestamp=timestamp, operator_name=operator_name, obsNum=obsNum, keywords=keywords, entry=entry)
    if ctx.triggered_id == 'problem-btn':
        lost_time = log_time(args[19])
        lost_time_details = {f'lost_time_{label.lower()}': args[i+20] for i, label in enumerate(['Weather', 'Icing', 'Power', 'Observers', 'Other'])}
        add_log_entry(timestamp=timestamp, operator_name=operator_name, lost_time=lost_time, **lost_time_details)
    if ctx.triggered_id == 'restart-btn':
        restart_time = log_time(args[9])
        add_log_entry(timestamp=timestamp, operator_name=operator_name, restart_time=restart_time)
    if ctx.triggered_id == 'shutdown-btn':
        shutdown_time = log_time(args[10])
        add_log_entry(timestamp=timestamp, operator_name=operator_name, shutdown_time=shutdown_time)
    if ctx.triggered_id == 'observer-btn':
        observers_list = ', '.join(args[25]) if args[25] else ''
        observers_other = args[26] if args[26] else ''
        observers_name = observers_other + ','+ observers_list if observers_other else observers_list
        add_log_entry(timestamp=timestamp, operator_name=operator_name, observers_name=observers_name)
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

# update user-table when delete user
@app.callback(
    Output('user-table', 'rowData', allow_duplicate=True),
    Input('delete-user-btn', 'n_clicks'),
    State('user-table', 'selectedRows'),
    prevent_initial_call=True)
def update_user_table(delete_clicks, selected_row):
    if ctx.triggered_id == 'delete-user-btn' and selected_row:
        print('selected_row:', selected_row)
        for row in range(0, len(selected_row)):
            username = selected_row[row]['Username']
            delete_user(username)
        return fetch_all_users()
    return no_update


# update and display user-table when manage user button is clicked
@app.callback(
    Output('user-table', 'rowData', allow_duplicate=True),
    Output('user-details','style'),
    Input('manage-users-btn', 'n_clicks'),
    prevent_initial_call=True
)
def update_user_table(manage_clicks):
    if ctx.triggered_id is None:
        raise PreventUpdate
    if ctx.triggered_id == 'manage-users-btn':
        return fetch_all_users(), {'display': 'block'}
    return no_update, {'display': 'none'}


# add user in the database when save button is clicked
@app.callback(
    Output('user-table', 'rowData', allow_duplicate=True),
    Output('add-user-modal', 'is_open', allow_duplicate=True),
    Output('add-user-status', 'is_open'),
    Output('add-user-status', 'children'),
    Output('add-username', 'value'),
    Output('add-email', 'value'),
    Output('add-password', 'value'),
    Output('add-confirm-password', 'value'),
    Input('add-user-btn', 'n_clicks'),
    Input('add-user', 'n_clicks'),
    State('add-username', 'value'),
    State('add-email', 'value'),
    State('add-is-admin', 'value'),
    State('add-password', 'value'),
    State('add-confirm-password', 'value'),
    prevent_initial_call=True)
def add_user_to_db(add_user_click, save_user_click,username, email, is_admin,password, confirm_password):
    if ctx.triggered_id is None:
        raise PreventUpdate
    if ctx.triggered_id == 'add-user-btn':
        return no_update, True, no_update, '', '', '', '', ''
    if ctx.triggered_id == 'add-user':
        if not username or not email or not password or not confirm_password:
            return no_update, no_update, True,'Please fill in all the fields', no_update, no_update, no_update, no_update
        if exist_user(username):
            return no_update, no_update, True,'User already exists', '', no_update, no_update, no_update
        if exist_email(email):
            return no_update, True, True,'Email already exists', no_update, '', no_update, no_update
        if password != confirm_password:
            return no_update, True, True,'Passwords do not match', no_update, no_update, '', ''
        if username and email and password and confirm_password:
            is_admin = True if is_admin else False
            add_user(username=username, email=email, password=password, is_admin=is_admin, create_at=current_time())
            return fetch_all_users(), False, True,'User added successfully', '', '', '', ''
    return no_update, no_update, no_update, '', '', '', '', ''

if __name__ == '__main__':
    init_db()
    create_admin_user()
    app.run_server(debug=True, dev_tools_props_check=False, threaded=False)
