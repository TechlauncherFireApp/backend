from domain.entity.diet_requirement import DietRequirement
from domain.type.dietary import DietaryRequirements


def save_dietary_requirements(session, user_id, dietary_requirements: DietaryRequirements):
    diet = session.query(DietRequirement).filter(DietRequirement.user_id == user_id).first()

    if not diet:
        # Create a new Diet object if none exists
        diet = DietRequirement(user_id=user_id)

    print(diet)
    # Set the values for the relevant attributes based on the dietary requirements
    for restriction in dietary_requirements.restrictions:
        if restriction.key == 'halal':
            diet.halal = True
        elif restriction.key == 'vegetarian':
            diet.vegetarian = True
        elif restriction.key == 'vegan':
            diet.vegan = True
        elif restriction.key == 'nut_allergy':
            diet.nut_allergy = True
        elif restriction.key == 'shellfish_allergy':
            diet.shellfish_allergy = True
        elif restriction.key == 'gluten_intolerance':
            diet.gluten_intolerance = True
        elif restriction.key == 'kosher':
            diet.kosher = True
        elif restriction.key == 'lactose_intolerance':
            diet.lactose_intolerance = True
        elif restriction.key == 'diabetic':
            diet.diabetic = True
        elif restriction.key == 'egg_allergy':
            diet.egg_allergy = True
        elif restriction.key == 'other':
            diet.other = dietary_requirements.custom_restrictions
        session.add(diet)
        session.flush()
    return diet


# def from_dietary_requirements(diet_args):
#     dic_diet = DietaryRequirements
#     for arg in vars(diet_args):
#         if getattr(diet_args, arg) == 'halal':
#
#     return dic_diet
