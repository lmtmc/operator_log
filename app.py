# todo if click report a problem show the reason form
# todo if the problem is fixed, click the fixed button
# todo if leave the site click the leave button
import dash
import dash_auth
from dash import html, dcc, Input, Output, State, no_update, ctx, Patch, ALL, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import pandas as pd
import datetime
from layout import (navbar,arrival_time,instrument_status,status_update,
                    form_choice, form_input, table_modal,reason_form)
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
                prevent_initial_callbacks="initial_duplicate")

hide = {'display': 'none'}
show = {'display': 'block'}

# Layout of the app
app.layout = dbc.Container([

    navbar,
    arrival_time,
    instrument_status,
    reason_form,
    status_update,
    dcc.Store(id='data-save', data={}, storage_type='memory'),
], id='page-content', className='mt-5')

instruments = ['rsr', 'sequoia', 'toltec', 'one_mm']

# if arrive button is clicked, show the instrument status form and the status update container
@app.callback(
    Output('instrument-status-check', 'style', allow_duplicate=True),
    Output('arrival-btn', 'disabled', allow_duplicate=True),
    Output('status-container', 'style', allow_duplicate=True),
    Output('leave-btn', 'disabled', allow_duplicate=True),
    Output('report-problem-btn', 'disabled', allow_duplicate=True),
    Output('arrival-status', 'children', allow_duplicate=True),
    Input('arrival-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_arrival_click(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate

    arrived_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        new_log = Log(timestamp=arrived_time, arrival_time=arrived_time,
                      shutdown_time='', rsr=False, sequoia=False, toltec=False, one_mm=False,
                      lost_time_start='', lost_time_end='', lost_time_weather='', lost_time_icing='',
                      lost_time_power='', lost_time_observers='', lost_time_other='')
        session.add(new_log)
        session.commit()
        print('add arrival time to the database')
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return show, True, show, False, False, f'Arrive at {arrived_time}'
# if instrument status button is clicked, save the instrument status in the database
@app.callback(
    Output('instrument-status', 'children', allow_duplicate=True),
    Input('instrument-status-btn', 'n_clicks'),
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
        new_log = Log(timestamp=datetime.datetime.now(), arrival_time='', shutdown_time='', **instrument_statuses,
                      lost_time_start='', lost_time_end='', lost_time_weather='', lost_time_icing='',
                      lost_time_power='', lost_time_observers='', lost_time_other='')
        session.add(new_log)
        session.commit()
        print('add instrument status to the database')
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return f'Instruments Checked {", ".join([f"{k} is ready" if v else f"{k} is not ready" for k, v in instrument_statuses.items()])}'

# if report a problem button is clicked, show the reason form
@app.callback(
    Output('reason-form', 'style', allow_duplicate=True),
    Output('reason-report', 'disabled', allow_duplicate=True),
    Output('fixed-btn', 'disabled', allow_duplicate=True),
    Input('report-problem-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_report_problem_click(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    return show, False, True

# if report button is clicked, save the reason and report time in the database and enable the fixed button, disable the report button
labels = ['Weather', 'Icing', 'Power', 'Observer', 'Other']
lost_state = [State(f"lost-{label.lower()}", 'value') for label in labels]
@app.callback(
    Output('fixed-btn', 'disabled'),
    Output('reason-report', 'disabled'),
    Output('problem-status', 'children'),
    Output('data-save', 'data',allow_duplicate=True),
    Input('reason-report', 'n_clicks'),
    State('data-save', 'data'),
    lost_state,
    prevent_initial_call=True
)
def handle_problem_submission(n_clicks, data_save, *args):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    # Format the report time as a string
    report_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        print(args)
        new_log = Log(timestamp=report_time, arrival_time='', shutdown_time='', rsr='', sequoia='', toltec='',
                      one_mm='', lost_time_start=report_time, lost_time_end='',
                      lost_time_weather=args[0], lost_time_icing=args[1],lost_time_power=args[2],
                      lost_time_observers=args[3], lost_time_other=args[4])
        session.add(new_log)
        session.commit()
    except Exception as e:
        session.rollback()
        print("Error occurred:", e)

    new_status = f'Problem reported at {report_time}. Reason: {", ".join([f"{labels[i]}: {args[i]}" for i in range(5) if args[i]])}'
    problem_status_message = data_save.get('problem_reported', [])
    print(problem_status_message)
    problem_status_message.append(new_status)
    data_save['problem_reported'] = problem_status_message

    status_component = html.Div([html.Div(message, className='mb-3') for message in problem_status_message])

    # Ensure the return statement matches the number of Output components
    return False, True, status_component, data_save

# if fixed button is clicked, save the fixed time and inputs in the database and hide the reason form
@app.callback(
    Output('reason-form', 'style', allow_duplicate=True),
    Output('problem-status', 'children', allow_duplicate=True),
    Output('data-save', 'data',allow_duplicate=True),
    Input('fixed-btn', 'n_clicks'),
    State('data-save', 'data'),
    lost_state,
    prevent_initial_call=True
)
def handle_fixed_click(n_clicks, data_save, *args):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    fixed_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Correctly using datetime object for timestamp
        fixed_time = datetime.datetime.now()
        new_log = Log(timestamp=fixed_time, arrival_time='', shutdown_time='', rsr=False, sequoia=False, toltec=False,
                      one_mm=False, lost_time_start='', lost_time_end='', lost_time_weather=args[0],
                      lost_time_icing=args[1],lost_time_power=args[2], lost_time_observers=args[3], lost_time_other=args[4])
        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    new_fixed_status = f'Fixed at {fixed_time} {", ".join([f"{labels[i]}: {args[i]}" for i in range(5) if args[i]])}'

    problem_status_message = data_save.get('problem_reported', [])

    problem_status_message.append(new_fixed_status)

    data_save['problem_reported'] = problem_status_message
    status_component = html.Div([html.Div(message, className='mb-3') for message in problem_status_message])
    return hide, status_component, data_save

# if leave button is clicked, save the leave time in the database and show the arrival button
# clear all the selected values
@app.callback(
    Output('leave-btn', 'disabled'),
    Output('leave-status', 'children'),
    Output('leave-status', 'style'),
    Output('report-problem-btn', 'disabled'),
    Output('instrument-status-check', 'style'),
    Output('reason-form', 'style'),
    Input('leave-btn', 'n_clicks'),
    prevent_initial_call=True
)
def handle_leave_click(n_clicks):
    if n_clicks is None or n_clicks == 0:
        raise PreventUpdate
    leave_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        new_log = Log(timestamp=leave_time, arrival_time='', shutdown_time=leave_time, rsr=False, sequoia=False, toltec=False,
                      one_mm=False, lost_time_start='', lost_time_end='', lost_time_weather='', lost_time_icing='',
                      lost_time_power='', lost_time_observers='', lost_time_other='')
        session.add(new_log)
        session.commit()
    except Exception as e:
        # Rollback in case of exception
        session.rollback()
        print("Error occurred:", e)
    return True, f'Leave at {leave_time}', show, True, hide,hide

if __name__ == '__main__':
    app.run_server(debug=True)