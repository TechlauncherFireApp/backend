from flask_restful import fields

id_model = {
    'id': fields.String,
}
role_model = {
    'id': fields.Integer,
    'code': fields.String,
    'name': fields.String,
    'created': fields.DateTime(attribute='insert_date_time', dt_format='iso8601'),
    'updated': fields.DateTime(attribute='update_date_time', dt_format='iso8601'),
    'deleted': fields.String(attribute='deleted'),
}


