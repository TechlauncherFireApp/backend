
from domain.entity.diet_requirement import DietRequirement
from domain import session_scope

from application import app  # Import the app instance from your application.py

with app.app_context():
    with session_scope() as session:
        # Test Case 1
        diet_requirement1 = DietRequirement(
            user_id=2,
            diet_id=2,
            halal=False,
            vegetarian=True,
            vegan=False,
            nut_allergy=False,
            shellfish_allergy=False,
            gluten_intolerance=True,
            kosher=False,
            lactose_intolerance=True,
            diabetic=True,
            egg_allergy=False,
            other="without oil"
        )

        # Test Case 2
        diet_requirement2 = DietRequirement(
            user_id=3,
            diet_id=3,
            halal=False,
            vegetarian=False,
            vegan=True,
            nut_allergy=False,
            shellfish_allergy=True,
            gluten_intolerance=False,
            kosher=False,
            lactose_intolerance=False,
            diabetic=False,
            egg_allergy=False,
            other=""
        )
        session.add(diet_requirement1)
        session.add(diet_requirement2)
        session.commit()

print("Diet requirement records added.")
