from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from webapp.models import db

SelfService = TypeVar("SelfService", bound="Service")

class Service(db.Model):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    valid_id = Column(Integer, nullable=False)
    comments = Column(String, nullable=True)
    create_time = Column(DateTime, nullable=False)
    create_by = Column(Integer, nullable=False)
    change_time = Column(DateTime, nullable=False)
    change_by = Column(Integer, nullable=False)
    type_id = Column(Integer, nullable=True)
    criticality = Column(String, nullable=True)

    @classmethod
    def get(cls: SelfService, service_id: int) -> SelfService:
        """Obtener el servicio por su ID
        
        Parameters
        ----------
        service_id: int
            ID del service_id
        
        Returns
        -------
        Service
            Un objeto del tipo Service
        """
        return db.session.query(cls).get(service_id)

    @classmethod
    def all(cls: SelfService) -> List[SelfService]:
        """Obtener todos los servicios

        Returns
        -------
        List[Service]
            Una lista de objetos Service
        """
        return db.session.query(cls).all()