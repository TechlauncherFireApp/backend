from operator import or_

from domain import User, Qualification, UserRole, Role
from repository.diet_requirement_repository import get_dietary_requirements


def get_volunteer(session, volunteer_id):
    return session.query(User) \
        .filter(User.id == volunteer_id) \
        .first()


def get_roles_for_user(user, session):
    roles = session.query(Role.name) \
        .join(UserRole, Role.id == UserRole.role_id) \
        .filter(UserRole.user_id == user['ID']) \
        .all()

    user['possibleRoles'] = [x[0] for x in roles]
    user_role = user['role'].value
    if 0 <= user_role <= 2:
        user['role'] = user_role
    else:
        user['role'] = -1


def get_qualifications_for_user(user, session):
    quals = session.query(Qualification.name) \
        .filter(Qualification.id.in_(user['qualifications'])) \
        .all()
    user['qualification'] = [x[0] for x in quals]


def list_volunteers(session, volunteer_id=None):
    users = session.query(User.id.label("ID"),
                         User.role.label('role'),
                         User.first_name.label('firstName'),
                         User.last_name.label('lastName'),
                         User.email.label('email'),
                         User.mobile_number.label('mobileNo'),
                         User.preferred_hours.label('prefHours'),
                         User.experience_years.label('expYears'),
                         User.qualifications.label('qualifications'),
                         User.availabilities.label('availabilities'))\
        .filter(or_(User.id == volunteer_id, volunteer_id == None))\
        .all()

    rtn = []
    # Set their roles
    for user in users:
        user = user._asdict()
        get_roles_for_user(user, session)
        get_qualifications_for_user(user, session)
        rtn.append(user)

    return rtn


def set_availabilities(session, volunteer_id, availability_json):
    volunteer = session.query(User) \
        .filter(User.id == volunteer_id) \
        .first()
    volunteer.availabilities = availability_json


def set_preferred_hours(session, volunteer_id, preferred_hours):
    volunteer = session.query(User) \
        .filter(User.id == volunteer_id) \
        .first()
    volunteer.preferred_hours = preferred_hours


def get_volunteer_info(session, volunteer_id):
    """
    Load the information required.
    The information included the user id, role, first namd, last name, email, mobile number, qualification
    and dietary requirement
    """
    users = session.query(User.id.label("ID"),
                         User.role.label('role'),
                         User.first_name.label('firstName'),
                         User.last_name.label('lastName'),
                         User.email.label('email'),
                         User.mobile_number.label('mobileNo'),
                         User.preferred_hours.label('prefHours'),
                         User.experience_years.label('expYears'),
                         User.qualifications.label('qualifications'),
                         User.availabilities.label('availabilities'))\
        .filter(User.id == volunteer_id)

    rtn = []
    for user in users:
        user = user._asdict()
        get_roles_for_user(user, session)
        get_qualifications_for_user(user, session)
        diet = get_dietary_requirements(session, user['ID'])
        if diet is not None:
            user['halal'] = diet.halal
            user['vegetarian'] = diet.vegetarian
            user['vegan'] = diet.vegan
            user['nut_allergy'] = diet.nut_allergy
            user['shellfish_allergy'] = diet.shellfish_allergy
            user['gluten_intolerance'] = diet.gluten_intolerance
            user['kosher'] = diet.kosher
            user['lactose_intolerance'] = diet.lactose_intolerance
            user['diabetic'] = diet.diabetic
            user['egg_allergy'] = diet.egg_allergy
            user['custom_restrictions'] = diet.other
        rtn.append(user)
    return rtn
