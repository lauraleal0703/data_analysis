from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import BLOB
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from .dynamic_field import DynamicField

from typing import TypeVar, List

from . import db

SelfDynamicFieldValue = TypeVar("SelfDynamicFieldValue", bound="DynamicFieldValue")

class DynamicFieldValue(db.Base):
    __tablename__ = 'dynamic_field_value'
    id = Column(Integer, primary_key=True)
    field_id = Column(Integer, ForeignKey("dynamic_field.id"), nullable=False)
    object_id = Column(String, nullable=False)
    value_text = Column(String)
    value_date = Column(Integer, nullable=True)
    value_int = Column(Integer, nullable=True)

    field: DynamicField = relationship("DynamicField", lazy=True)

    @classmethod
    def all(cls: SelfDynamicFieldValue) -> List[SelfDynamicFieldValue]:
        """Obtener todos los datos

        Returns
        -------
        List[SelfDynamicFieldValue]
            Una lista de objetos SelfDynamicFieldValue
        """
        return db.session.query(cls).all()
    
    #############################################################
	#############QUERY ID OFENSA QRADAR##########################
	#############################################################

    @classmethod
    def get_offense_id(cls: SelfDynamicFieldValue,
		ticket_id: int
    ) -> str:
        """Dado el ID del ticket obtener el ID de QRadar

		field_id = 36 "name": ticketOfensa
		
		Parameters
		----------
		ticket_id: int
			ID del ticket

		Returns
		-------
		str
			ID de la ofensa en qradar.
		"""
        query = db.session.query(cls).filter(
			cls.object_id == ticket_id,
            cls.field_id == 36
        ).first()
        if query:
            query: SelfDynamicFieldValue
            return query.value_text

