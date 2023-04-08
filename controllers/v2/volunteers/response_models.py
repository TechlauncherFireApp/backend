from flask_restful import fields

volunteer_listing_model = {
    'ID': fields.String,
    'firstName': fields.String,
    'lastName': fields.String,
    'qualification': fields.List(fields.String),
}