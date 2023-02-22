from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import BLOB
from sqlalchemy import DateTime

from typing import TypeVar, List

from . import db

SelfDynamicField = TypeVar("SelfDynamicField", bound="DynamicField")

class DynamicField(db.Base):
    __tablename__ = 'dynamic_field'
    id = Column(Integer, primary_key=True)
    internal_field = Column(Integer, nullable=False, default=0)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    field_order = Column(Integer, nullable=False)
    field_type = Column(String, nullable=False)
    object_type = Column(String, nullable=False)
    config = Column(BLOB)
    valid_id = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    create_by = Column(Integer, nullable=False)
    change_time = Column(DateTime, nullable=False)
    change_by = Column(Integer, nullable=False)

    @classmethod
    def all(cls: SelfDynamicField) -> List[SelfDynamicField]:
        """Obtener todos los datos

        Returns
        -------
        List[DynamicField]
            Una lista de objetos DynamicField
        """
        return db.session.query(cls).all()