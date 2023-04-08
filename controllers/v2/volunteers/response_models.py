from flask_restful import fields

volunteer_personal_info = {
    'ID': fields.String,
    'first_name': fields.String,
    'last_name': fields.String,
    'mobile_number': fields.String,
    'email': fields.String,
    'possible_roles': fields.String,
    'qualification': fields.List(fields.String),
    'restrictions': {
        'halal': fields.Boolean,
        'vegetarian': fields.Boolean,
        'vegan': fields.Boolean,
        'nut_allergy': fields.Boolean,
        'shellfish_allergy': fields.Boolean,
        'gluten_intolerance': fields.Boolean,
        'kosher': fields.Boolean,
        'lactose_intolerance': fields.Boolean,
        'diabetic': fields.Boolean,
        'egg_allergy': fields.Boolean
    },
    'custom_restrictions': fields.String
}
