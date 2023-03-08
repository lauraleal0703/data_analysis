from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey


from typing import TypeVar, List

from webapp.models import db

SelfQueue = TypeVar("SelfQueue", bound="Queue")

class Queue(db.Model):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    group_id = Column(Integer, nullable=False)
    unlock_timeout = Column(Integer, nullable=True)
    first_response_time = Column(Integer, nullable=True)
    first_response_notify = Column(Integer, nullable=True)
    update_time = Column(Integer, nullable=True)
    update_notify = Column(Integer, nullable=True)
    solution_time = Column(Integer, nullable=True)
    solution_notify = Column(Integer, nullable=True)
    system_address_id = Column(Integer, nullable=False)
    calendar_name = Column(String, nullable=True)
    default_sign_key = Column(String, nullable=True)
    salutation_id = Column(Integer, nullable=False)
    signature_id = Column(Integer, nullable=False)
    follow_up_id = Column(Integer, nullable=False)
    follow_up_lock = Column(Integer, nullable=False)
    comments = Column(String, nullable=True)
    valid_id = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    create_by = Column(Integer, nullable=False)
    change_time = Column(DateTime, nullable=False)
    change_by = Column(Integer, nullable=False)


    @classmethod
    def get(cls: SelfQueue, queue_id: int) -> SelfQueue:
        """Obtener el servicio por su ID
        
        Parameters
        ----------
        queue_id: int
            ID del queue
        
        Returns
        -------
        Queue
            Un objeto del tipo Queue
        """
        return db.session.query(cls).get(queue_id)

    @classmethod
    def all(cls: SelfQueue) -> List[SelfQueue]:
        """Obtener todos las colas

        Returns
        -------
        List[Queue]
            Una lista de objetos Queue
        """
        return db.session.query(cls).all()