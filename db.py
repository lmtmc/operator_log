# db.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Engine is the starting point for any SQLAlchemy application.
# It’s “home base” for the actual database and its DBAPI, delivered to the SQLAlchemy application
# through a connection pool and a Dialect, which describes how to talk to a specific kind of database/DBAPI combination.
log_engine = create_engine('sqlite:///log.db', poolclass=NullPool)
user_engine = create_engine('sqlite:///user.db', poolclass=NullPool)

# Session is a factory for creating new Session objects.
LogSession = sessionmaker(bind=log_engine)
UserSession = sessionmaker(bind=user_engine)

# Base class for declarative class definitions
LogBase = declarative_base()
UserBase = declarative_base()

def current_time():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def current_time_input():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M')

def log_time(current_time):
    if current_time is None:
        return ''
    else:
        return datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')

class Log(LogBase):
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
    observers_name = Column(String, default='')

    def __init__(self, timestamp=current_time(), operator_name='', arrival_time='', shutdown_time='', rsr='', sequoia='', toltec='',
                 one_mm='', obsNum='', keywords='', entry='',lost_time='', restart_time='', lost_time_weather='',
                 lost_time_icing='', lost_time_power='',lost_time_observers='', lost_time_other='', observers_name=''):
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
        self.observers_name = observers_name


    def __repr__(self):
        return (f'<Log {self.timestamp} {self.operator_name} {self.arrival_time} {self.shutdown_time} {self.rsr} '
                f'{self.sequoia} {self.toltec} {self.one_mm} {self.obsNum} {self.keywords} {self.entry} {self.lost_time}'
                f' {self.restart_time} {self.lost_time_weather} {self.lost_time_icing} {self.lost_time_power} '
                f'{self.lost_time_observers} {self.lost_time_other} {self.observers_name}>')

class User(UserBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, default='')
    email = Column(String, unique=True, nullable=False, default='')
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False) # Admin flag
    create_at = Column(String, default=current_time)

    def __init__(self, username, email, password, is_admin, create_at=current_time()):
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)
        self.is_admin = is_admin
        self.create_at = create_at

    def __repr__(self):
        return f'<User {self.username} {self.email} >'

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

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
    'lost_time_other': 'Others',
    'observers_name': 'Observers'
}
def init_db():
    try:
        LogBase.metadata.create_all(bind=log_engine)
        UserBase.metadata.create_all(bind=user_engine)
        print("Databases initialized")
    except Exception as e:
        print("Error occurred:", e)

def add_user(**kwargs):
    session = UserSession()
    new_user = User(**kwargs)
    session.add(new_user)
    session.commit()
    print("User added")
    session.close()

    # with UserSession() as session:
    #     new_user = User(**kwargs)
    #     session.add(new_user)
    #     try:
    #         session.commit()
    #         print("User added")
    #         return True
    #     except Exception as e:
    #         session.rollback()
    #         print("Error occurred:", e)
    #         return False

user_column_mapping = {
    'id': 'ID',
    'create_at': 'Created At',
    'username': 'Username',
    'email': 'Email',
    'is_admin': 'Is Admin',
}
def fetch_all_users():
    with UserSession() as session:
        users = session.query(User).all()
        user_data = [{user_column_mapping[key]: value for key, value in user.__dict__.items() if key in user_column_mapping}
                     for user in users]
        return user_data

def update_user_password(username, password):
    with UserSession() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.password_hash = User.hash_password(password)
            try:
                session.commit()
                return True
            except Exception as e:
                session.rollback()
                print("Error occurred:", e)
                return False

def fetch_user_by_username(username):
    with UserSession() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            return user
        else:
            return None

def exist_user(email):
    with UserSession() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            return True
        else:
            return False

def exist_email(email):
    with UserSession() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            return True
        else:
            return False
def validate_user(username, password):
    with UserSession() as session:
        user = session.query(User).filter_by(username=username).first()
        if user and user.verify_password(password):
            return True
        else:
            return False

def delete_user(username):
    with UserSession() as session:
        user = session.query(User).filter_by(username=username).first()
        session.delete(user)
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)
            return False

def add_log_entry(**kwargs):
    with LogSession() as session:
        new_log = Log(**kwargs)
        session.add(new_log)
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)
            return False

# if specify a number n, return the last n log entries, otherwise return all log entries
def fetch_log_data(n):
    with LogSession() as session:
        if session.query(Log).count() == 0:
            return []
        if n is None:
            query_result = session.query(Log).all()
        else:
            query_result = session.query(Log).order_by(Log.timestamp.desc()).limit(n).all()
        log_data = [{column_mapping[key]: value for key, value in log.__dict__.items() if key in column_mapping}
                    for log in query_result]
        return log_data

def create_admin_user():
    if not fetch_user_by_username('admin'):
        add_user(username='admin',email='xhuang@umass.edu',password='admin',is_admin=True)
    else:
        print("Admin user already exists")

init_db()
create_admin_user()
