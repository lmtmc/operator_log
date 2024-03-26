#todo when save arrival clicked, datatable not udpated until refresh
# Enter comment not working
import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update, dash_table
from dash.exceptions import PreventUpdate
import dash_auth
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
import time
from layout import (login_page, dash_app_page, setting_page,navbar, prefix, instruments,data_column,
                    admin_page,observer_arrive, instrument_form,problem_form,resume_form, ObsNum_form,shutdown_time)
from db import (exist_user, exist_email,delete_user,validate_user, add_user, update_user,update_user_password,fetch_user_by_username,
                fetch_all_users,add_log_entry, fetch_log_data,init_db,create_admin_user,
                current_time, current_timestamp,log_time)
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
                server = server, title='LMT Observer Log',
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

# Layout of the app

app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(navbar, className='mb-5'),
    html.Div(id='page-content'),
],)

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
        return login_page
    elif pathname.endswith(f'/{prefix}/settings'):
        if current_user.is_authenticated:
            return setting_page
        else:
            return login_page
    elif current_user.is_authenticated:
        return dash_app_page
    return login_page


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

# update tab content when the tab is opened
@app.callback(Output('tab-content', 'children'),
                Input('tabs', 'value'),
                )
def update_tab_content(active_tab):
    if active_tab is None:
        raise PreventUpdate
    if active_tab == 'tab-arrive':
        return observer_arrive
    elif active_tab == 'tab-instrument':
        return instrument_form
    elif active_tab == 'tab-problem':
        return problem_form
    elif active_tab == 'tab-resume':
        return resume_form
    elif active_tab == 'tab-obsnum':
        return ObsNum_form
    elif active_tab == 'tab-shutdown':
        return shutdown_time
    return no_update

# update the observer name when the tab is opened
@app.callback(Output('observer-name-label', 'children'),
              Output('observers-checklist', 'options'),
              Input('tabs', 'value'),
              )
def update_observer(active_tab):
    if active_tab == 'tab-arrive' and current_user.is_authenticated:
        users = fetch_all_users()
        # exclude the admin and current user from the observer checklist
        registered_users = [{'label': user['Username'], 'value': user['Username']}
                for user in users if user['Username'] != current_user.id and not user['Is Admin']]
        return f'Welcome, {current_user.id} !', registered_users
    return no_update

# update the log table when the tab is opened
@app.callback(Output('log-table', 'rowData', allow_duplicate=True),
              Output('log-table-div', 'style'),
              Input('view-btn', 'n_clicks'),
                prevent_initial_call=True)
def update_log_table(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return fetch_log_data(10), {'display': 'block'}

@app.callback(
    Output('log-table', 'rowData', allow_duplicate=True),
    Input('arrival-btn', 'n_clicks'),
    [
        State('observers-checklist', 'value'),
        State('observer-name-input', 'value'),
        State({'type':'dynamic-time-input', 'index':'arrival-time-input'}, 'value'),
        State({'type':'dynamic-time-input','index':'weather-time-input'}, 'value'),
        State('sky-input', 'value'),
        State('tau-input', 'value'),
        State('t-input', 'value'),
        State('rh-input', 'value'),
        State('wind-input', 'value'),
        State('weather-other-input', 'value'),
        State('main-plan-input', 'value'),
    ],
    prevent_initial_call=True
)
def save_arrival(n_clicks, observers_other, others, arrival_time, weather_time, sky, tau, t, rh, wind, weather_other,main_plan):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    # join the names of the observers
    observers_other = ','.join(observers_other) if observers_other else ''
    add_log_entry(timestamp=current_timestamp(), observer_account=current_user.id, other_observers=observers_other,others=others,
                  arrival_time=log_time(arrival_time),weather_time=log_time(weather_time), sky=sky, tau=tau, t=t, rh=rh, wind=wind, weather_other=weather_other,
                  main_plan=main_plan)
    return fetch_log_data(10)

# save instrument status when the instrument button is clicked
@app.callback(
    Output('log-table', 'rowData', allow_duplicate=True),
    Input('instrument-btn', 'n_clicks'),
    [
        State({'type':'dynamic-time-input','index':'start-time-input'}, 'value'),
        State('instrument-note', 'value')
    ] +
    [
        State(instrument, 'value') for instrument in instruments
    ] +
    [
        State({'type':'dynamic-time-input', 'index': f'{instrument}-time-input'},'value') for instrument in instruments
    ] +
    [
        State(f'{instrument}-note', 'value') for instrument in instruments
    ],
    prevent_initial_call=True
)
def save_instrument(n_clicks, start_time, observer_notes, *instrument_statuses):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    # Assuming instrument_statuses are packed as [status, note, time] for each instrument
    statuses, times, notes = instrument_statuses[0:4], instrument_statuses[4:8], instrument_statuses[8:12]
    statuses = ["Ready" if status is not None and status[0] == 1 else "Not Ready" for status in statuses]
    times = [log_time(time) for time in times]
    add_log_entry(timestamp=current_timestamp(), observer_account=current_user.id, start_time=log_time(start_time), notes=observer_notes,
                  toltec=statuses[0], toltec_time=times[0], toltec_note=notes[0],
                  rsr=statuses[1], rsr_time=times[1], rsr_note=notes[1],
                    sequoia=statuses[2], sequoia_time=times[2], sequoia_note=notes[2],
                    one_mm=statuses[3], one_mm_time=times[3], one_mm_note=notes[3])
    # Fetch and return the updated log data for the table
    return fetch_log_data(10)
# save the problem log when the problem button is clicked
@app.callback(
    Output('log-table', 'rowData', allow_duplicate=True),
    Input('problem-btn', 'n_clicks'),
    [
        State({'type':'dynamic-time-input','index':'problem-log-time'}, 'value'),
        State('lost-weather', 'value'),
        State('lost-icing', 'value'),
        State('lost-power', 'value'),
        State('lost-observers', 'value'),
        State('lost-other', 'value'),
    ],
    prevent_initial_call=True
)
def save_problem(n_clicks, problem_time, weather, icing, power, observers, other):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    add_log_entry(timestamp=current_timestamp(), observer_account=current_user.id,pause_time=log_time(problem_time),
                  weather=weather, icing=icing, power=power, observers_not_available=observers, other_reason=other)
    return fetch_log_data(10)

# save the resume log when the resume button is clicked
@app.callback(
    Output('log-table', 'rowData', allow_duplicate=True),
    Input('resume-btn', 'n_clicks'),
    [
        State({'type':'dynamic-time-input','index':'resume-time-input'}, 'value'),
        State('resume-comment', 'value'),
    ],
    prevent_initial_call=True
)
def save_resume(n_clicks, resume_time, comment):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    add_log_entry(timestamp=current_timestamp(), observer_account=current_user.id,resume_time=log_time(resume_time), comment=comment)
    return fetch_log_data(10)

# save user note when the note button is clicked
@app.callback(
    Output('log-table', 'rowData', allow_duplicate=True),
    Input('note-btn', 'n_clicks'),
    [
        State('obsnum-input', 'value'),
        State('keyword-input', 'value'),
        State('keyword-checklist', 'value'),
        State('entry-input', 'value'),
    ],
    prevent_initial_call=True
)
def save_note(n_clicks, obsNum, keyword, keyword_checklist, entry):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    keyword_checklist = ', '.join(keyword_checklist) if keyword_checklist else ''
    if keyword == 'None':
        keyword = ''
    keywords = keyword + ', ' + keyword_checklist if keyword else keyword_checklist
    add_log_entry(timestamp=current_timestamp(), observer_account=current_user.id,obsNum=obsNum, keywords=keywords, entry=entry)
    return fetch_log_data(10)

# save the shutdown log when the shutdown button is clicked
@app.callback(
    Output('log-table', 'rowData', allow_duplicate=True),
    Input('shutdown-btn', 'n_clicks'),
    [
        State({'type':'dynamic-time-input','index':'shutdown-time-input'}, 'value'),
    ],
    prevent_initial_call=True
)
def save_shutdown(n_clicks, shutdown_time):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    add_log_entry(timestamp=current_timestamp(), observer_account=current_user.id,shutdown_time=log_time(shutdown_time))
    return fetch_log_data(10)


# dynamic time now button
@app.callback(
    [
        Output({'type':'dynamic-time-input','index':ALL}, 'value', allow_duplicate=True),
    ],
    [
        Input({'type':'dynamic-time-now-btn','index':ALL}, 'n_clicks'),
    ],
    prevent_initial_call=True
)
def dynamic_time_now(*args):
    triggered_id = ctx.triggered_id
    if not triggered_id:
        raise PreventUpdate
    index = triggered_id['index']
    value = [current_time() if output['id']['index']==index else no_update for output in ctx.outputs_list[0]]
    return [value]



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

# if selected rows are not empty, show the delete and update buttons
@app.callback(
    Output('delete-user-btn', 'disabled'),
    # Output('update-user-btn', 'disabled'),
    Input('user-table', 'selectedRows'),
    prevent_initial_call=True
)
def show_delete_update_btn(selected_rows):
    if selected_rows:
        return False
    return True


# update user-table when delete user
@app.callback(
    Output('user-table', 'rowData', allow_duplicate=True),
    Input('delete-user-btn', 'n_clicks'),
    State('user-table', 'selectedRows'),
    prevent_initial_call=True)
def update_user_table(delete_clicks, selected_row):
    if ctx.triggered_id == 'delete-user-btn' and selected_row:
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
