from flask_restful import fields

shift = {
    'shiftId': fields.Integer,
    'title': fields.String,
    'start': fields.DateTime(dt_format='iso8601'),
    'end': fields.DateTime(dt_format='iso8601')
}
