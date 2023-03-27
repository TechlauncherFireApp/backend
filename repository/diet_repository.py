from domain.entity.diet_requirement import DietRequirement


def save_dietary_requirements(session, user_id, dietary_requirements):
    """
    A helper function for upload the data to the database.
    This function will map the argument from the frontend with the statement in the database
    Then using the session to update the database
    This function is allowed to change the dietary requirement for the user by providing the user_id

    Parameters:
        session: A SQLAlchemy Session for the query.
        user_id: The user_id to identify create a new dietary requirement or
                change the current dietary requirement in the database
        dietary_requirements: The parser contains the data required for update

    Returns:
        True if the data is updated; False if the data is not upload
    """
    # Change the diet requirement in the database
    diet = session.query(DietRequirement).filter(DietRequirement.user_id == user_id).first()

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
