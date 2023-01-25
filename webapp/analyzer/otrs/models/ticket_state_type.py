from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from . import db

SelfTicketStateType = TypeVar("SelfTicketStateType", bound="TicketStateType")

class TicketStateType(db.Base):
	__tablename__ = 'ticket_state_type'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	comments = Column(String, nullable=True)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	@classmethod
	def get(cls: SelfTicketStateType, ticket_state_type_id: int) -> SelfTicketStateType:
		"""Obtener el tipo del estado del ticket por su ID
		
		Parameters
		----------
		ticket_state_type_id: int
			ID del ticket_state_type_id
		
		Returns
		-------
		TicketStateType
			Un objeto del tipo TicketStateType
		"""
		return db.session.query(cls).get(ticket_state_type_id)
	
	@classmethod
	def all(cls: SelfTicketStateType) -> List[SelfTicketStateType]:
		"""Obtener todos los tipos de los estados del ticket
	
		Returns
		-------
		List[SelfTicketStateType]
			Una lista de objetos SelfTicketStateType
		"""
		return db.session.query(cls).all()

