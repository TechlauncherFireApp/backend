from typing import List


class DietaryRestriction:
    """
    This is a class to define the Dietary Restriction
    """
    def __init__(self, key: str, display_name: str):
        """
        The constructor for DietaryRestriction class.
        Parameters:
            key (str): This is a key for the restriction can find on the database
            display_name (str): The display name show on the front-end
        """
        self.key = key
        self.display_name = display_name


class DietaryRequirements:
    """
    This is a class to define the Dietary Requirements
    This is the input format for storing the dietary requirements in the database
    This is the output format for returning the dietary requirements to the frontend
    """
    def __init__(self, restrictions: List[DietaryRestriction], custom_restrictions: str = None):
        """
        The constructor for DietaryRequirements class.
        Parameters:
            restrictions (list): A list of DietaryRestriction that containing only true DietaryRestrictions
            custom_restrictions (str): The customised restrictions required for the user
        """
        self.restrictions = restrictions
        self.custom_restrictions = custom_restrictions
