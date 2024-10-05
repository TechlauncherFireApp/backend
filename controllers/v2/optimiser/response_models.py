from flask_restful import fields

optimiser_response_model = {
    'message': fields.String,
    'result': fields.Raw
}
