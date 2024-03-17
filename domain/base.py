from contextlib import contextmanager
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from services.secrets import SecretService

# secret = SecretService(f"database/{os.environ.get('env', 'dev')}/fireapp")

# Configure Session
Session = sessionmaker()
if os.environ.get("SQLALCHEMY_DATABASE_URI"):
    Engine = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI"))
else:
    Engine = create_engine('mysql+mysqldb://{0}:{1}@{2}:{3}/{4}'.format(os.environ.get('username'),
                                                                        os.environ.get('password'),
                                                                        os.environ.get('host'),
                                                                        os.environ.get('port'),
                                                                        os.environ.get('dbname')), echo=False)
Session.configure(bind=Engine)

# Configure Declarative Base for ORM
Base = declarative_base()


@event.listens_for(Base, 'before_insert')
def receive_before_update(mapper, connection, target):
    target.insert_date_time = datetime.now()
    target.update_date_time = datetime.now()


@event.listens_for(Base, 'before_update')
def receive_before_update(mapper, connection, target):
    target.update_date_time = datetime.now()


Base.metadata.create_all(Engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
