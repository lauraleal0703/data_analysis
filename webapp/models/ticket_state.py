from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from typing import TypeVar, List

from webapp.models import db
from webapp.models.ticket_state_type import TicketStateType


SelfTicketState = TypeVar("SelfTicketState", bound="TicketState")

class TicketState(db.Model):
	__tablename__ = 'ticket_state'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	comments = Column(String, nullable=True)
	type_id = Column(Integer, ForeignKey("ticket_state_type.id"), nullable=False)
	valid_id = Column(Integer, nullable=False)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	type_state: TicketStateType = relationship("TicketStateType", lazy=True)

	@classmethod
	def get(cls: SelfTicketState, ticket_state_id: int) -> SelfTicketState:
		"""Obtener el estado del ticket por su ID
		
		Parameters
		----------
		ticket_priority_id: int
			ID del ticket_state_id
		
		Returns
		-------
		TicketState
			Un objeto del tipo TicketState
		"""
		return db.session.query(cls).get(ticket_state_id)
	
	@classmethod
	def all(cls: SelfTicketState) -> List[SelfTicketState]:
		"""Obtener todos los estados del ticket
	
		Returns
		-------
		List[SelfTicketState]
			Una lista de objetos SelfTicketState
		"""
		return db.session.query(cls).all()

