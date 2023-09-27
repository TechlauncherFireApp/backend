from flask_restful import fields

dietary_restriction = {
    "key": fields.String,
    "display_name": fields.String
}

volunteer_dietary_requirement = {
    "custom_restrictions": fields.String,
    "restrictions": fields.List(fields.Nested(dietary_restriction))
}

dietary_requirement_options = {
    "options": fields.List(fields.Nested(dietary_restriction))
}