from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

from services.optimiser import Optimiser
"""
run the below command to run this file
export username='user'
export password='password'
export host='127.0.0.1'
export port='3306'
export dbname='db'
python -m services.optimiser.testing.testing_scheduler
"""


# get database connection details from environment variables
username = os.getenv('DB_USERNAME', 'user')
password = os.getenv('DB_PASSWORD', 'password')
host = os.getenv('DB_HOST', 'localhost')
port = os.getenv('DB_PORT', '3306')
dbname = os.getenv('DB_NAME', 'db')

# database URL
DATABASE_URL = f"mysql+pymysql://{username}:{password}@{host}:{port}/{dbname}"

# set up the database session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# specify the request_id and whether to run in debug mode
request_id = int(os.getenv('REQUEST_ID', 1))  # Example request ID, can be overridden by environment variable
debug = os.getenv('DEBUG_MODE', 'True').lower() == 'true'  # Set to False to disable debug output

# create and run the optimiser
optimiser = Optimiser(session=session, request_id=request_id, debug=debug)
result = optimiser.solve()

print("Optimisation Result:")
print(result)

# close the session
session.close()

print("Optimisation complete.")