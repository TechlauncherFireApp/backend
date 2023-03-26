from flask import Blueprint
from flask_restful import Api

v2_bp = Blueprint('volunteer_all', __name__)
v2_api = Api(v2_bp)
