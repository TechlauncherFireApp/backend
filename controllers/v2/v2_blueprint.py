from flask import Blueprint
from flask_restful import Api

v2_bp = Blueprint('v2', __name__)
v2_api = Api(v2_bp)

v2_info = Blueprint('info', __name__)
v2_info_api = Api(v2_info)
