from domain.entity.diet_requirement import DietRequirement


def get_dietary_requirements(session, user_id):
    diet_requirement = session.query(DietRequirement).filter(DietRequirement.user_id == user_id).first()
    if diet_requirement:
        session.expunge(diet_requirement)
    return diet_requirement
