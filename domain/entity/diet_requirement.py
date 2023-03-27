from sqlalchemy import Column, Integer, ForeignKey, Boolean, UniqueConstraint, String
from sqlalchemy.orm import relationship

from domain import Base


class DietRequirement(Base):
    __tablename__ = 'diet_requirement'
    diet_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    halal = Column(Boolean, nullable=False, default=0)
    vegetarian = Column(Boolean, nullable=False, default=0)
    vegan = Column(Boolean, nullable=False, default=0)
    nut_allergy = Column(Boolean, nullable=False, default=0)
    shellfish_allergy = Column(Boolean, nullable=False, default=0)
    gluten_intolerance = Column(Boolean, nullable=False, default=0)
    kosher = Column(Boolean, nullable=False, default=0)
    lactose_intolerance = Column(Boolean, nullable=False, default=0)
    diabetic = Column(Boolean, nullable=False, default=0)
    egg_allergy = Column(Boolean, nullable=False, default=0)
    other = Column(String, nullable=False, default=0)

    UniqueConstraint(diet_id, user_id)

    user = relationship("User")
