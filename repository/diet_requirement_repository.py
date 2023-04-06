from domain.entity.diet_requirement import DietRequirement


def get_dietary_requirements(session, user_id):

    diet_requirement = session.query(DietRequirement).filter(DietRequirement.user_id == user_id).first()
    return diet_requirement
