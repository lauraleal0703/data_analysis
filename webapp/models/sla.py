from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from webapp.models import db


SelfSla = TypeVar("SelfSla", bound="Sla")

class Sla(db.Model):
    __tablename__ = 'sla'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    calendar_name = Column(String, nullable=True)
    first_response_time = Column(Integer, nullable=False)
    first_response_notify = Column(Integer, nullable=True)
    update_time = Column(Integer, nullable=False)
    update_notify = Column(Integer, nullable=True)
    solution_time = Column(Integer, nullable=False)
    solution_notify = Column(Integer, nullable=True)
    valid_id = Column(Integer, nullable=False)
    comments = Column(String, nullable=True)
    create_time = Column(DateTime, nullable=False)
    create_by = Column(Integer, nullable=False)
    change_time = Column(DateTime, nullable=False)
    change_by = Column(Integer, nullable=False)
    type_id = Column(Integer, nullable=True)
    min_time_bet_incidents = Column(Integer, nullable=True)

    @classmethod
    def get(cls: SelfSla, sla_id: int) -> SelfSla:
        """Obtener el sla por su ID
        
        Parameters
        ----------
        sla_id: int
            ID del sla_id
        
        Returns
        -------
        Sla
            Un objeto del tipo Sla
        """
        return db.session.query(cls).get(sla_id)

    @classmethod
    def all(cls: SelfSla) -> List[SelfSla]:
        """Obtener todos los sla

        Returns
        -------
        List[Sla]
            Una lista de objetos Sla
        """
        return db.session.query(cls).all()