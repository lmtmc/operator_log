# todo revise the database
# todo add more columns
import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update, dash_table
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from layout import (navbar,operator_arrive, shutdown_time, instrument_status,problem_form,restart_form,
                    ObsNum_form)
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
    operator_name = Column(String)
    arrival_time = Column(String)
    shutdown_time = Column(String)
    rsr = Column(String)
    sequoia = Column(String)
    toltec = Column(String)
    one_mm = Column(String)
    obsNum = Column(String)
    keywords = Column(String)
    entry = Column(String)
    lost_time = Column(String)
    restart_time = Column(String)
    lost_time_weather = Column(String)
    lost_time_icing = Column(String)
    lost_time_power = Column(String)
    lost_time_observers = Column(String)
    lost_time_other = Column(String)


    def __init__(self, timestamp, operator_name, arrival_time, shutdown_time, rsr, sequoia, toltec, one_mm, obsNum,
                 keywords, entry,lost_time, restart_time, lost_time_weather, lost_time_icing, lost_time_power,
                 lost_time_observers, lost_time_other):
        self.timestamp = timestamp
        self.operator_name = operator_name
        self.arrival_time = arrival_time
        self.shutdown_time = shutdown_time
        self.rsr = rsr
        self.sequoia = sequoia
        self.toltec = toltec
        self.one_mm = one_mm
        self.obsNum = obsNum
        self.keywords = keywords
        self.entry = entry
        self.lost_time = lost_time
        self.restart_time = restart_time
        self.lost_time_weather = lost_time_weather
        self.lost_time_icing = lost_time_icing
        self.lost_time_power = lost_time_power
        self.lost_time_observers = lost_time_observers
        self.lost_time_other = lost_time_other


    def __repr__(self):
        return (f'<Log {self.timestamp} {self.operator_name} {self.arrival_time} {self.shutdown_time} {self.rsr} '
                f'{self.sequoia} {self.toltec} {self.one_mm} {self.obsNum} {self.keywords} {self.entry} {self.lost_time}'
                f' {self.restart_time} {self.lost_time_weather} {self.lost_time_icing} {self.lost_time_power} '
                f'{self.lost_time_observers} {self.lost_time_other} >')
Base.metadata.create_all(bind=engine)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'],
                prevent_initial_callbacks="initial_duplicate", suppress_callback_exceptions=True)

hide = {'display': 'none'}
show = {'display': 'block'}

data_column = ['ID', 'Timestamp', 'Operator Name', 'Arrival Time', 'Shutdown Time', 'RSR', 'SEQUOIA', 'TolTEC', '1mm',
                 'ObsNum', 'Keyword', 'Entry', 'Lost Time', 'Restart Time', 'Lost Time Weather', 'Lost Time Icing', 'Lost Time Power',
                 'Lost Time Observers', 'Lost Time Other']
def fetch_log_data():
    log_count = session.query(Log).count()
    if log_count == 0:
        return pd.DataFrame(columns=data_column)

    query_result = session.query(Log).order_by(Log.timestamp.desc()).limit(10)

    # mapping database column names to the table column names
    column_mapping = {
        'id': 'ID',
        'timestamp': 'Timestamp',
        'operator_name': 'Operator Name',
        'arrival_time': 'Arrival Time',
        'shutdown_time': 'Shutdown Time',
        'rsr': 'RSR',
        'sequoia': 'SEQUOIA',
        'toltec': 'TolTEC',
        'one_mm': '1mm',
        'obsNum': 'ObsNum',
        'keywords': 'Keyword',
        'entry': 'Entry',
        'lost_time': 'Lost Time',
        'restart_time': 'Restart Time',
        'lost_time_weather': 'Lost Time Weather',
        'lost_time_icing': 'Lost Time Icing',
        'lost_time_power': 'Lost Time Power',
        'lost_time_observers': 'Lost Time Observers',
        'lost_time_other': 'Lost Time Other'
    }
    # print('query_result',query_result)
    log_data = pd.DataFrame([{column_mapping[key]: value for key, value in log.__dict__.items() if key in column_mapping}
                             for log in query_result])
    log_data = log_data[data_column]
    return log_data
def generate_csv(data):
    return data.to_csv(index=False, encoding='utf-8-sig')

columns = [{'name': '1mm' if col == 'one_mm' else col.capitalize(), 'id': col} for col in fetch_log_data().columns]
log_history = dbc.Card(
            [
                dbc.CardHeader([
                    dbc.Row([
                        dbc.Col(html.H3("Log History (10 most recent entries)"), style={'textAlign': 'center'},
                                className='mt-3'),
                        dbc.Col(html.Button('Download Log', id='download-button', n_clicks=0, className='download-button'),
                                width='auto'),
                    ], align='center', justify='center', className='mt-3')]),
                dbc.CardBody(
                    [
                        html.Div(dash_table.DataTable(
                            id='log-table',
                            columns=columns,
                            data=fetch_log_data().to_dict('records'),
                            style_table={'overflowX': 'auto', 'height': '350px'},
                            style_data_conditional=[
                                {
                                    'if': {'row_index': 'odd'},
                                    'backgroundColor': 'rgb(248, 248, 248)'
                                }
                            ],
                        ), className='mt-3 ml-5dash-spreadsheet-container ', id='status-container'),
                    ]
                )
            ], className='mt-5'
        ),

def log_time(current_time):
    if current_time is None:
        return ''
    else:
        return datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
def current_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def current_time_input():
    return datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')

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

instruments = ['rsr', 'sequoia', 'toltec', '1mm']

# if the arrive-now button is clicked, save the current time in the arrival time input
# if the problem-now button is clicked, save the current time in the problem time input
# if the shutdown-now button is clicked, save the current time in the shutdown time input
# if the restart-now button is clicked, save the current time in the restart time input
@app.callback(
    Output('arrival-time-input', 'value'),
    Output('problem-log-time', 'value'),
    Output('shutdown-time-input', 'value'),
    Output('restart-time-input', 'value'),
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


# if arrive button is clicked, save the arrival time in the database and update the status-container
@app.callback(
    Output('log-table', 'data', allow_duplicate=True),
    Output('operator-name-input', 'value'),
    Input('arrival-btn', 'n_clicks'),
    State('operator-name-input', 'value'),
    State('arrival-time-input', 'value'),
    prevent_initial_call=True
)
def handle_arrival_click(n_clicks, operator_name, arrival_time):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    with Session() as session:
        print('operator_name',operator_name,'arrival_time',arrival_time)
        try:
            new_log = Log(timestamp=current_time(),
                          operator_name=operator_name,
                          arrival_time=log_time(arrival_time),
                          shutdown_time='',
                          rsr='',
                          sequoia='',
                          toltec='',
                          one_mm='',
                          obsNum='',
                          keywords='',
                          entry='',
                          lost_time='',
                          restart_time='',
                          lost_time_weather='',
                          lost_time_icing='',
                          lost_time_power='',
                          lost_time_observers='',
                          lost_time_other='')
            session.add(new_log)
            session.commit()
        except Exception as e:
            # Rollback in case of exception
            session.rollback()
            print("Error occurred:", e)
    return fetch_log_data().to_dict('records'), ''
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
        print('instrument_statuses',instrument_statuses)
        new_log = Log(timestamp=current_time(),
                          operator_name='',
                          arrival_time='',
                          shutdown_time='',
                          rsr=instrument_statuses['rsr'],
                          sequoia=instrument_statuses['sequoia'],
                          toltec=instrument_statuses['toltec'],
                          one_mm=instrument_statuses['1mm'],
                          obsNum='',
                          keywords='',
                          entry='',
                          lost_time='',
                          restart_time='',
                          lost_time_weather='',
                          lost_time_icing='',
                          lost_time_power='',
                          lost_time_observers='',
                          lost_time_other='')
        session.add(new_log)
        session.commit()
        print('add instrument status to the database','new_log',new_log)
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return fetch_log_data().to_dict('records')

# if save entry button is clicked, save the obsNum, keywords, and entry in the database
@app.callback(
    Output('log-table', 'data', allow_duplicate=True),
    Input('entry-btn', 'n_clicks'),
    State('obsnum-input', 'value'),
    State('keyword-input', 'value'),
    State('keyword-checklist', 'value'),
    State('entry-input', 'value'),
    prevent_initial_call=True
)
def handle_entry_click(n_clicks, obsNum, keyword, keyword_checklist, entry):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    keywords = keyword+ ', '+', '.join(keyword_checklist) if keyword_checklist else keyword
    try:
        new_log = Log(timestamp=current_time(),
                        operator_name='',
                        arrival_time='',
                        shutdown_time='',
                        rsr='',
                        sequoia='',
                        toltec='',
                        one_mm='',
                        obsNum=obsNum,
                        keywords=keywords,
                        entry=entry,
                        lost_time='',
                        restart_time='',
                        lost_time_weather='',
                        lost_time_icing='',
                        lost_time_power='',
                        lost_time_observers='',
                        lost_time_other='')
        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return fetch_log_data().to_dict('records')

# if report button is clicked, save the reason and report time in the database and enable the fixed button, disable the report button
labels = ['Weather', 'Icing', 'Power', 'Observers', 'Other']
lost_state = [State(f"lost-{label.lower()}", 'value') for label in labels]
lost_output = [Output(f"lost-{label.lower()}", 'value', allow_duplicate=True) for label in labels]
@app.callback(
    [Output('log-table', 'data', allow_duplicate=True)]+lost_output,
    Input('problem-btn', 'n_clicks'),
    [State('problem-log-time', 'value')] + lost_state,
    prevent_initial_call=True
)
def handle_problem_submission(n_clicks, problem_time, *args):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    # Format the report time as a string
    try:
        new_log = Log(
            timestamp=current_time(),
            operator_name='',
            arrival_time='',
            shutdown_time='',
            rsr='',
            sequoia='',
            toltec='',
            one_mm='',
            obsNum='',
            keywords='',
            entry='',
            lost_time=log_time(problem_time),
            restart_time='',
            lost_time_weather=args[0],
            lost_time_icing=args[1],
            lost_time_power=args[2],
            lost_time_observers=args[3],
            lost_time_other=args[4])


        session.add(new_log)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error occurred:", e)
    # Ensure the return statement matches the number of Output components
    return [fetch_log_data().to_dict('records')] + ['', '', '', '', '']

# if fixed button is clicked, save the restart time
@app.callback(
    [Output('log-table', 'data', allow_duplicate=True)]+lost_output,
    Input('restart-btn', 'n_clicks'),
    State('restart-time-input', 'value'),
    prevent_initial_call=True
)
def handle_restart_click(n_clicks, restart_time):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    try:
        new_log = Log(
            timestamp=current_time(),
            operator_name='',
            arrival_time='',
            shutdown_time='',
            rsr='',
            sequoia='',
            toltec='',
            one_mm='',
            obsNum='',
            keywords='',
            entry='',
            lost_time='',
            restart_time=log_time(restart_time),
            lost_time_weather='',
            lost_time_icing='',
            lost_time_power='',
            lost_time_observers='',
            lost_time_other=''
        )

        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return [fetch_log_data().to_dict('records')] + ['', '', '', '', '']

# if shutdown button is clicked, save the shutdown time in the database and show the arrival button
# clear all the selected values
@app.callback(
    Output('log-table', 'data'),
    Input('shutdown-btn', 'n_clicks'),
    State('shutdown-time-input', 'value'),
    prevent_initial_call=True
)
def handle_shutdown_click(n_clicks, shutdown_time):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    try:
        new_log = Log(timestamp=current_time(),
                      operator_name='',
                      arrival_time='',
                      shutdown_time=log_time(shutdown_time),
                      rsr='', sequoia='',
                      toltec='', one_mm='', obsNum='', keywords='', entry='', lost_time='', restart_time='',
                      lost_time_weather='', lost_time_icing='', lost_time_power='', lost_time_observers='', lost_time_other='')
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