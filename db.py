# db.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import PIL.Image as Image
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
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M')

def current_timestamp():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def log_time(current_time):
    if current_time is None:
        return ''

    # First, try parsing with the ISO 8601 format
    try:
        return datetime.datetime.strptime(current_time, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M')
    except ValueError:
        # If the first attempt fails, try the alternative format
        try:
            return datetime.datetime.strptime(current_time, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M')
        except ValueError:
            # If both attempts fail, the format is unrecognized
            raise ValueError(f"time data '{current_time}' does not match any of the expected formats")

database_column = ['id', 'timestamp', 'observer_account', 'other_observers', 'others', 'arrival_time', 'weather_time',
                      'sky', 'tau', 't', 'rh', 'wind', 'weather_other', 'main_plan', 'start_time', 'notes','toltec', 'toltec_time', 'toltec_note',
                     'rsr', 'rsr_time', 'rsr_note', 'sequoia', 'sequoia_time', 'sequoia_note', 'one_mm', 'one_mm_time',
                     'one_mm_note', 'pause_time', 'weather', 'icing', 'power', 'observers_not_available', 'other_reason',
                     'image', 'resume_time', 'comment', 'obsNum', 'keywords', 'entry', 'shutdown_time']

data_column = ["ID", "Timestamp", "Observer Account", "Other Observers", "Other", "Arrival Time",
               "Weather Record Time", "Sky", "Tau", "T", "RH", "Wind", "Other Weather",
               "Main Plan",
                "System Start Time", "Notes",
               "TolTEC", "TolTEC Status Time", "TolTEC Note",
               "RSR", "RSR Status Time", "RSR Note",
               "SEQUOIA", "SEQUOIA Status Time", "SEQUOIA Note",
               "1mm", "1mm Status Time", "1mm Note",
               "Pause Time", "Weather", "Icing", "Power", "Observers Not Available", "Others","Image",
               "Resume Time", "Comment",
               "ObsNum", "Keyword", "Entry",
               "Shutdown Time"] # 41 columns

column_mapping = dict(zip(database_column, data_column))
class Log(LogBase):
    __tablename__ = 'log'
    id = Column(Integer, primary_key=True)
    timestamp = Column(String, default=current_timestamp)
    observer_account = Column(String, default='')
    other_observers = Column(String, default='')
    others = Column(String, default='')
    arrival_time = Column(String, default=current_time)
    weather_time = Column(String, default='')
    sky = Column(String, default='')
    tau = Column(String, default='')
    t = Column(String, default='')
    rh = Column(String, default='')
    wind = Column(String, default='')
    weather_other = Column(String, default='')
    main_plan = Column(String, default='')
    notes = Column(String, default='')
    start_time = Column(String, default='')
    toltec = Column(String, default='')
    toltec_time = Column(String, default='')
    toltec_note = Column(String, default='')
    rsr = Column(String, default='')
    rsr_time = Column(String, default='')
    rsr_note = Column(String, default='')
    sequoia = Column(String, default='')
    sequoia_time = Column(String, default='')
    sequoia_note = Column(String, default='')
    one_mm = Column(String, default='')
    one_mm_time = Column(String, default='')
    one_mm_note = Column(String, default='')
    pause_time = Column(String, default='')
    weather = Column(String, default='')
    icing = Column(String, default='')
    power = Column(String, default='')
    observers_not_available = Column(String, default='')
    other_reason = Column(String, default='')
    image = Column(String, default='')
    resume_time = Column(String, default='')
    comment = Column(String, default='')
    obsNum = Column(String, default='')
    keywords = Column(String, default='')
    entry = Column(String, default='')
    shutdown_time = Column(String, default='')

class User(UserBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False, default='')
    email = Column(String, unique=True, nullable=False, default='')
    password_hash = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False) # Admin flag
    create_at = Column(String, default=current_time)
    is_default_password = Column(Boolean, default=True)

    def __init__(self, username, email, password, is_admin, create_at=current_time(), is_default_password=True):
        self.username = username
        self.email = email
        self.password_hash = self.hash_password(password)
        self.is_admin = is_admin
        self.create_at = create_at
        self.is_default_password = is_default_password

    def __repr__(self):
        return f'<User {self.username} {self.email} >'

    @staticmethod
    def hash_password(password):
        return generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


def init_db():
    try:
        LogBase.metadata.create_all(bind=log_engine)
        UserBase.metadata.create_all(bind=user_engine)
        print("Databases initialized")
    except Exception as e:
        print("Error occurred:", e)

def add_user(**kwargs):
    if exist_email(kwargs['email']):
        print("Email already exists")
        return False

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
            user.is_default_password = False
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
def fetch_user_by_email(email):
    with UserSession() as session:
        user = session.query(User).filter_by(email=email).first()
        if user:
            return user
        else:
            return None
def exist_user(username):
    with UserSession() as session:
        user = session.query(User).filter_by(username=username).first()
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
def validate_user(email, password):
    with UserSession() as session:
        user = session.query(User).filter_by(email=email).first()
        if not user:
            print("User not found")
            return False
        return user.verify_password(password)


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
        if email != user.email and exist_email(email):
            print("Email already exists")
            return False

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
        log_data = []
        for log in query_result:
            log_entry = {column_mapping[key]: value for key, value in log.__dict__.items() if key in column_mapping}
            if 'Image' in log_entry and log_entry['Image'] is not None:
                if os.path.exists(log_entry['Image']):
                    log_entry['Image'] = Image.open(log_entry['Image'])
            log_data.append(log_entry)
        return log_data

def create_admin_user():
    if not fetch_user_by_email('xiahuang@umass.edu'):
        add_user(username='admin',email='xiahuang@umass.edu',password='admin',is_admin=True)
    else:
        print("Admin user already exists")
#
# init_db()
# create_admin_user()
