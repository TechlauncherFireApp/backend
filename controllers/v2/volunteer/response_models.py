from flask_restful import fields
from controllers.v2.v2_blueprint import v2_api

volunteer_listing_model = v2_api.model('Model', {
    'ID': fields.String,
    'firstName': fields.String,
    'lastName': fields.String,
    'qualifications': fields.List(fields.String),
})
