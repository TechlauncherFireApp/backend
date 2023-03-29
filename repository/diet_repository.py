from domain.entity.diet_requirement import DietRequirement


def save_dietary_requirements(session, user_id, dietary_requirements):
    """
    Stores dietary requirements for the given user to the database.
    Any existing requirements for that user will be overwritten.

    Parameters:
        session: A SQLAlchemy Session for the query.
        user_id: An id for the user who are requesting to edit
        dietary_requirements: Requirements that will be stored in the database

    Returns:
        True if the data is updated; False if the data is not upload
    """
    # Change the diet requirement in the database
    diet = session.query(DietRequirement).filter(DietRequirement.user_id == user_id).first()

    # initialize the dietary requirement
    diet.halal = False
    diet.vegetarian = False
    diet.vegan = False
    diet.nut_allergy = False
    diet.shellfish_allergy = False
    diet.gluten_intolerance = False
    diet.kosher = False
    diet.lactose_intolerance = False
    diet.diabetic = False
    diet.egg_allergy = False
    diet.other = ""

    if not diet:
        # Create a new diet requirement object if none exists
        diet = DietRequirement(user_id=user_id)

    # Set the values for the relevant attributes based on the dietary requirements
    if dietary_requirements.restrictions is not None:
        for restriction in dietary_requirements.restrictions:
            if restriction.key["key"] == 'halal':
                diet.halal = True
            elif restriction.key["key"] == 'vegetarian':
                diet.vegetarian = True
            elif restriction.key["key"] == 'vegan':
                diet.vegan = True
            elif restriction.key["key"] == 'nut_allergy':
                diet.nut_allergy = True
            elif restriction.key["key"] == 'shellfish_allergy':
                diet.shellfish_allergy = True
            elif restriction.key["key"] == 'gluten_intolerance':
                diet.gluten_intolerance = True
            elif restriction.key["key"] == 'kosher':
                diet.kosher = True
            elif restriction.key["key"] == 'lactose_intolerance':
                diet.lactose_intolerance = True
            elif restriction.key["key"] == 'diabetic':
                diet.diabetic = True
            elif restriction.key["key"] == 'egg_allergy':
                diet.egg_allergy = True
    if dietary_requirements.custom_restrictions != "":
        diet.other = dietary_requirements.custom_restrictions

    # load the data to the database
    session.add(diet)
    session.flush()

    return diet