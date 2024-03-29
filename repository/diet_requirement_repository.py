from domain.entity.diet_requirement import DietRequirement


def get_formatted_dietary_requirements(session, user_id):
    diet_requirement_dict = diet_requirement_to_dict(get_dietary_requirements(session, user_id))

    restrictions = []
    for key, value in diet_requirement_dict.items():
        if key not in ['diet_id', 'user_id', 'other'] and value:
            display_name = key.replace('_', ' ').title()
            restrictions.append({"key": key, "display_name": display_name})

    return {
        "custom_restrictions": diet_requirement_dict.get('other', ''),
        "restrictions": restrictions
    }


def get_dietary_requirements(session, user_id):
    diet_requirement = session.query(DietRequirement).filter(DietRequirement.user_id == user_id).first()
    if diet_requirement:
        session.expunge(diet_requirement)
    return diet_requirement


def diet_requirement_to_dict(diet_requirement):
    if not diet_requirement:
        return {}
    return {
        'diet_id': diet_requirement.diet_id,
        'user_id': diet_requirement.user_id,
        'halal': bool(diet_requirement.halal),
        'vegetarian': bool(diet_requirement.vegetarian),
        'vegan': bool(diet_requirement.vegan),
        'nut_allergy': bool(diet_requirement.nut_allergy),
        'shellfish_allergy': bool(diet_requirement.shellfish_allergy),
        'gluten_intolerance': bool(diet_requirement.gluten_intolerance),
        'kosher': bool(diet_requirement.kosher),
        'lactose_intolerance': bool(diet_requirement.lactose_intolerance),
        'diabetic': bool(diet_requirement.diabetic),
        'egg_allergy': bool(diet_requirement.egg_allergy),
        'other': diet_requirement.other
    }
