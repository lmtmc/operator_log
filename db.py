# db.py
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

engine = create_engine('sqlite:///log.db', echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

def current_time():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def current_time_input():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M')

def log_time(current_time):
    if current_time is None:
        return ''
    else:
        return datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

class Log(Base):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String, default=current_time)
    operator_name = Column(String, default='')
    arrival_time = Column(String, default='')
    shutdown_time = Column(String, default='')
    rsr = Column(String, default='')
    sequoia = Column(String, default='')
    toltec = Column(String, default='')
    one_mm = Column(String, default='')
    obsNum = Column(String, default='')
    keywords = Column(String, default='')
    entry = Column(String, default='')
    lost_time = Column(String, default='')
    restart_time = Column(String, default='')
    lost_time_weather = Column(String, default='')
    lost_time_icing = Column(String, default='')
    lost_time_power = Column(String, default='')
    lost_time_observers = Column(String, default='')
    lost_time_other = Column(String, default='')

    def __init__(self, timestamp=current_time(), operator_name='', arrival_time='', shutdown_time='', rsr='', sequoia='', toltec='',
                 one_mm='', obsNum='', keywords='', entry='',lost_time='', restart_time='', lost_time_weather='',
                 lost_time_icing='', lost_time_power='',lost_time_observers='', lost_time_other=''):
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
    'lost_time_weather': 'Weather',
    'lost_time_icing': 'Icing',
    'lost_time_power': 'Power',
    'lost_time_observers': 'Observers Not Available',
    'lost_time_other': 'Others'
}
def init_db():
    Base.metadata.create_all(bind=engine)


def get_session():
    return Session()

def add_log_entry(**kwargs):
    session = get_session()
    new_log = Log(**kwargs)
    session.add(new_log)
    try:
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print("Error occurred:", e)
        return False

def fetch_log_data():
    session = get_session()
    query_result = session.query(Log).order_by(Log.timestamp.desc()).limit(10).all()
    session.close()
    log_data = [{column_mapping[key]: value for key, value in log.__dict__.items() if key in column_mapping}
                for log in query_result]
    return log_data
