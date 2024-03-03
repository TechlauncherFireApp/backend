from flask_restful import fields

volunteer_unavailability_time = {
    'eventID': fields.Integer,
    'userID': fields.Integer,
    'title': fields.String,
    'startTime': fields.DateTime(dt_format='iso8601'),
    'endTime': fields.DateTime(dt_format='iso8601'),
    'periodicity': fields.Integer
}
