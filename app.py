# todo if click report a problem show the reason form
# todo if the problem is fixed, click the fixed button
# todo if leave the site click the leave button
import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from layout import (navbar,arrival_time, leave_time, instrument_status,table_modal,problem_form)
import json
from sqlalchemy import create_engine, ForeignKey, Column, Integer, String, CHAR, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base

# setup database
engine = create_engine('sqlite:///log.db', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()
class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String)
    arrival_time = Column(String)
    shutdown_time = Column(String)
    rsr = Column(String)
    sequoia = Column(String)
    toltec = Column(String)
    one_mm = Column(String)
    lost_time_start = Column(String)
    lost_time_end = Column(String)
    lost_time_weather = Column(String)
    lost_time_icing = Column(String)
    lost_time_power = Column(String)
    lost_time_observers = Column(String)
    lost_time_other = Column(String)

    def __init__(self, timestamp, arrival_time, shutdown_time, rsr, sequoia, toltec, one_mm, lost_time_start, lost_time_end, lost_time_weather, lost_time_icing, lost_time_power, lost_time_observers, lost_time_other):
        self.timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.arrival_time = arrival_time
        self.shutdown_time = shutdown_time
        self.rsr = rsr
        self.sequoia = sequoia
        self.toltec = toltec
        self.one_mm = one_mm
        self.lost_time_start = lost_time_start
        self.lost_time_end = lost_time_end
        self.lost_time_weather = lost_time_weather
        self.lost_time_icing = lost_time_icing
        self.lost_time_power = lost_time_power
        self.lost_time_observers = lost_time_observers
        self.lost_time_other = lost_time_other

    def __repr__(self):
        return (f"Log({self.arrival_time}, {self.shutdown_time}, {self.rsr}, {self.sequoia}, {self.toltec}, {self.one_mm}"
                f", {self.lost_time_start}, {self.lost_time_end}, {self.lost_time_weather}, {self.lost_time_icing}, "
                f"{self.lost_time_power}, {self.lost_time_observers}, {self.lost_time_other})")
Base.metadata.create_all(bind=engine)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True)

hide = {'display': 'none'}
show = {'display': 'block'}

# Layout of the app
app.layout = dbc.Container([

    navbar,
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children=[]),
])
def fetch_log_data():
    log_count = session.query(Log).count()
    if log_count == 0:
        return pd.DataFrame(columns=['id','timestamp', 'arrival_time', 'shutdown_time', 'rsr', 'sequoia', 'toltec', 'one_mm',
                                     'lost_time_start', 'lost_time_end', 'lost_time_weather', 'lost_time_icing',
                                     'lost_time_power', 'lost_time_observers', 'lost_time_other'])

    query_result = session.query(Log).order_by(Log.timestamp.desc()).limit(10)
    print('query_result',query_result)
    desired_order = ['id', 'timestamp', 'arrival_time', 'shutdown_time', 'rsr', 'sequoia', 'toltec', 'one_mm',
                 'lost_time_start', 'lost_time_end', 'lost_time_weather', 'lost_time_icing', 'lost_time_power',
                 'lost_time_observers', 'lost_time_other']
    log_data = pd.DataFrame([{key: value for key, value in log.__dict__.items() if key != '_sa_instance_state'} for log in query_result])

    return log_data[desired_order]
def generate_csv(data):
    return data.to_csv(index=False, encoding='utf-8-sig')

def enter_data():
    return html.Div([
        dbc.Row([
            dbc.Col(arrival_time,width='auto'),
            dbc.Col(instrument_status, width='auto'),
            dbc.Col(leave_time, width='auto'),
        ]),
        dbc.Row(dbc.Col(problem_form), ),
        html.Div(dash_table.DataTable(
            id='log-table',
            columns=[{'name': col, 'id': col} for col in fetch_log_data().columns],
            data=fetch_log_data().to_dict('records'),
            style_table={'overflowX': 'auto', 'maxHeight': '500px'},
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        ),className='mt-3 form-container', id='status-container'),
        table_modal,
        dcc.Download(id='download-log')
    ])

def search_layout():
    return html.Div([
        html.H3('Search')
    ])

def report_layout():
    return html.Div([
        html.H3('Report')
    ])

def log_time(current_time):
    if current_time is None:
        return ''
    else:
        return datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
def current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              prevent_initial_call=True)
def display_page(pathname):
    if pathname == '/enter-data' or pathname == '/':
        return enter_data()
    elif pathname == '/search':
        return search_layout()
    elif pathname == '/report':
        return report_layout()
    else:
        return enter_data()

instruments = ['rsr', 'sequoia', 'toltec', 'one_mm']

# if arrive button is clicked, save the arrival time in the database and update the status-container
@app.callback(
    Output('log-table', 'data', allow_duplicate=True),
    Input('arrival-btn', 'n_clicks'),
    State('arrival-time-input', 'value'),
    prevent_initial_call=True
)
def handle_arrival_click(n_clicks, arrival_time):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    print('input arrival time', arrival_time)
    try:
        new_log = Log(timestamp=current_time(), arrival_time=log_time(arrival_time),
                      shutdown_time='', rsr=False, sequoia=False, toltec=False, one_mm=False,
                      lost_time_start='', lost_time_end='', lost_time_weather='', lost_time_icing='',
                      lost_time_power='', lost_time_observers='', lost_time_other='')
        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return fetch_log_data().to_dict('records')
# if instrument status button is clicked, save the instrument status in the database
@app.callback(
    Output('log-table', 'data', allow_duplicate=True),
    Input('instrument-btn', 'n_clicks'),
    State(instruments[0], 'value'),
    State(instruments[1], 'value'),
    State(instruments[2], 'value'),
    State(instruments[3], 'value'),
    prevent_initial_call=True
)
def handle_instrument_status_click(n_clicks, *args):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    try:
        # Correctly using datetime object for timestamp
        instrument_statuses = {instruments[i]: 1 if args[i] is not None and args[i][0] == 1 else 0 for i in range(4)}
        new_log = Log(timestamp=current_time(), arrival_time='', shutdown_time='', **instrument_statuses,
                      lost_time_start='', lost_time_end='', lost_time_weather='', lost_time_icing='',
                      lost_time_power='', lost_time_observers='', lost_time_other='')
        session.add(new_log)
        session.commit()
        print('add instrument status to the database','new_log',new_log)
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return fetch_log_data().to_dict('records')

# if report a problem button is clicked, disable the report button and enable the fix button, if the problem is fixed
# if click the fixed button, enable the report button and disable the fixed button
@app.callback(
    Output('report-problem-btn', 'disabled'),
    Output('fixed-btn', 'disabled'),
    Input('report-problem-btn', 'n_clicks'),
    Input('fixed-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_problem_click(report_clicks, fixed_clicks):
    if ctx.triggered_id is None:
        raise PreventUpdate
    if ctx.triggered_id == 'report-problem-btn':
        return True, False
    if ctx.triggered_id == 'fixed-btn':
        return False, True

# if report button is clicked, save the reason and report time in the database and enable the fixed button, disable the report button
labels = ['Weather', 'Icing', 'Power', 'Observer', 'Other']
lost_state = [State(f"lost-{label.lower()}", 'value') for label in labels]
lost_output = [Output(f"lost-{label.lower()}", 'value', allow_duplicate=True) for label in labels]
@app.callback(
    [Output('log-table', 'data', allow_duplicate=True)]+lost_output,
    Input('report-problem-btn', 'n_clicks'),
    [State('problem-time', 'value')] + lost_state,
    prevent_initial_call=True
)
def handle_problem_submission(n_clicks, problem_time, *args):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    # Format the report time as a string
    try:
        new_log = Log(timestamp=current_time(), arrival_time='', shutdown_time='', rsr='', sequoia='', toltec='',
                      one_mm='', lost_time_start=log_time(problem_time), lost_time_end='',
                      lost_time_weather=args[0], lost_time_icing=args[1],lost_time_power=args[2],
                      lost_time_observers=args[3], lost_time_other=args[4])
        session.add(new_log)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error occurred:", e)
    # Ensure the return statement matches the number of Output components
    return [fetch_log_data().to_dict('records')] + ['', '', '', '', '']

# if fixed button is clicked, save the fixed time and inputs in the database and hide the reason form
@app.callback(
    [Output('log-table', 'data', allow_duplicate=True)]+lost_output,
    Input('fixed-btn', 'n_clicks'),
    [State('problem-time', 'value')] + lost_state,
    prevent_initial_call=True
)
def handle_fixed_click(n_clicks, problem_time, *args):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    fixed_time = datetime.datetime.strptime(problem_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
    try:
        new_log = Log(timestamp=current_time(), arrival_time='', shutdown_time='', rsr='', sequoia='', toltec='',
                      one_mm='', lost_time_start='', lost_time_end=log_time(problem_time), lost_time_weather=args[0],
                      lost_time_icing=args[1],lost_time_power=args[2], lost_time_observers=args[3], lost_time_other=args[4])
        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return [fetch_log_data().to_dict('records')] + ['', '', '', '', '']

# if leave button is clicked, save the leave time in the database and show the arrival button
# clear all the selected values
@app.callback(
    Output('log-table', 'data'),
    Input('leave-btn', 'n_clicks'),
    State('leave-time-input', 'value'),
    prevent_initial_call=True
)
def handle_leave_click(n_clicks, leave_time):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    try:
        new_log = Log(timestamp=current_time(), arrival_time='', shutdown_time=log_time(leave_time), rsr='', sequoia='', toltec='',
                      one_mm='', lost_time_start='', lost_time_end='', lost_time_weather='', lost_time_icing='',
                      lost_time_power='', lost_time_observers='', lost_time_other='')
        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return fetch_log_data().to_dict('records')


def save_log_data():
    log_data = fetch_log_data()
    log_csv = generate_csv(log_data)
    with open('log.csv', 'w') as f:
        f.write(log_csv)
    return 'log.csv'

# click the log history button, show the log history table
@app.callback(
    Output('table-container', 'is_open'),
    Output('modal-body-content', 'children'),
    Input('history-button', 'n_clicks'),
    Input('close-modal', 'n_clicks'),
    State('table-container', 'is_open'),
    prevent_initial_call=True
)
def handle_log_history_click(n1, n2, is_open):
    if n1 is None and n2 is None:
        raise PreventUpdate
    if n1 or n2:
        return not is_open,
    return no_update, no_update

# click the download log button, download the log db as a csv file
@app.callback(
    Output('download-log', 'data'),
    Input('download-button', 'n_clicks'),
    prevent_initial_call=True
)
def handle_download_log_click(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return dcc.send_file(save_log_data())

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_props_check=False)