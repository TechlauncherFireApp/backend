

from domain.entity.user import User

def update_dietary_requirements(session, user_id, args):
    """
Update the dietary requirements of a user.

Parameters:

session: database session
user_id: ID of the user
args: parameters containing dietary requirements
Returns:

True if the update is successful; False otherwise.
    """
    try:
        user = session.query(User).filter(User.id == user_id).one()
        user.dietary_restrictions = args['restrictions']
        user.custom_restrictions = args['custom_restrictions']
        session.commit()
        return True
    except Exception as e:
        print(f"Error updating dietary requirements: {e}")
        return False

def get_user_by_id(session, user_id):
    """
Find user by ID
:param session: database session
:param user_id: ID of the user
:return: if user is found, return the user object, otherwise return None
   """
    try:
        user = session.query(User).filter(User.id == user_id).one_or_none()
        return user
    except Exception as e:
        print(f"Error getting user by id: {e}")
        return None


