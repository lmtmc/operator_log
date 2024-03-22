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
    observer_account = Column(String, default='')
    other_observers = Column(String, default='')
    others = Column(String, default='')
    arrival_time = Column(String, default='')
    toltec = Column(String, default='')
    rsr = Column(String, default='')
    sequoia = Column(String, default='')
    one_mm = Column(String, default='')

    pause_time = Column(String, default='')
    weather = Column(String, default='')
    icing = Column(String, default='')
    power = Column(String, default='')
    observers_not_available = Column(String, default='')
    other_reason = Column(String, default='')

    resume_time = Column(String, default='')
    comment = Column(String, default='')

    obsNum = Column(String, default='')
    keywords = Column(String, default='')
    entry = Column(String, default='')

    shutdown_time = Column(String, default='')

    def __init__(self, timestamp=current_time(), observer_account='', other_observers='', others='', arrival_time='',
                 toltec='', rsr='', sequoia='', one_mm='', pause_time='', weather='', icing='',
                 power='', observer_not_available='', other_reason='', resume_time='', comment='', obsNum='', keywords='', entry='', shutdown_time=''):
        self.timestamp = timestamp
        self.observer_account = observer_account
        self.other_observers = other_observers
        self.others = others
        self.arrival_time = arrival_time
        self.toltec = toltec
        self.rsr = rsr
        self.sequoia = sequoia
        self.one_mm = one_mm
        self.pause_time = pause_time
        self.weather = weather
        self.icing = icing
        self.power = power
        self.observers_not_available = observer_not_available
        self.other_reason = other_reason
        self.resume_time = resume_time
        self.comment = comment
        self.obsNum = obsNum
        self.keywords = keywords
        self.entry = entry
        self.shutdown_time = shutdown_time

    def __repr__(self):
        return f'<Log {self.timestamp} {self.observer_account} {self.other_observers} {self.others} {self.arrival_time} {self.toltec} {self.rsr} {self.sequoia} {self.one_mm} {self.pause_time} {self.weather} {self.icing} {self.power} {self.observers_not_available} {self.other_reason} {self.resume_time} {self.comment} {self.obsNum} {self.keywords} {self.entry} {self.shutdown_time} >'

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

data_column = ["ID", "Timestamp", "Observer Account", "Other Observers", "Other", "Arrival Time",
               "TolTEC", "RSR", "SEQUOIA", "1mm", "Pause Time", "Weather", "Icing", "Power", "Observers Not Available", "Others",
               "Resume Time", "Comment", "ObsNum", "Keyword", "Entry", "Shutdown Time"]

column_mapping = {
    'id': data_column[0],
    'timestamp': data_column[1],
    'observer_account': data_column[2],
    'other_observers': data_column[3],
    'others': data_column[4],
    'arrival_time': data_column[5],
    'toltec': data_column[6],
    'rsr': data_column[7],
    'sequoia': data_column[8],
    'one_mm': data_column[9],
    'pause_time': data_column[10],
    'weather': data_column[11],
    'icing': data_column[12],
    'power': data_column[13],
    'observers_not_available': data_column[14],
    'other_reason': data_column[15],
    'resume_time': data_column[16],
    'comment': data_column[17],
    'obsNum': data_column[18],
    'keywords': data_column[19],
    'entry': data_column[20],
    'shutdown_time': data_column[21],
}
def init_db():
    try:
        LogBase.metadata.create_all(bind=log_engine)
        UserBase.metadata.create_all(bind=user_engine)
        print("Databases initialized")
    except Exception as e:
        print("Error occurred:", e)

def add_user(**kwargs):
    with UserSession() as session:
        new_user = User(**kwargs)
        session.add(new_user)
        try:
            session.commit()
            print("User added")
            return True
        except Exception as e:
            session.rollback()
            print("Error occurred:", e)
            return False

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

def update_user(username, email, is_admin, password=None):
    with UserSession() as session:
        user = session.query(User).filter_by(username=username).first()
        if user:
            user.email = email
            user.is_admin = is_admin
            if password:
                user.password_hash = User.hash_password(password)
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
