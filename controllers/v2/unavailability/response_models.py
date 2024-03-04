from flask_restful import fields

volunteer_unavailability_time = {
    'eventId': fields.Integer,
    'userId': fields.Integer,
    'title': fields.String,
    'start': fields.DateTime(dt_format='iso8601'),
    'end': fields.DateTime(dt_format='iso8601'),
    'periodicity': fields.Integer
}
