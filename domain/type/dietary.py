from typing import List


class DietaryRestriction:
    def __init__(self, key: str, display_name: str):
        self.key = key
        self.display_name = display_name


class DietaryRequirements:
    def __init__(self, restrictions: List[DietaryRestriction], custom_restrictions: str = None):
        self.restrictions = restrictions
        self.custom_restrictions = custom_restrictions
