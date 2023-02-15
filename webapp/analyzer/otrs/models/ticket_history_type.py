from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from . import db


SelfTicketHistoryType = TypeVar("SelfTicketHistoryType", bound="TicketHistoryType")

class TicketHistoryType(db.Base):
	__tablename__ = 'ticket_history_type'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	comments = Column(String, nullable=True)
	valid_id = Column(Integer, nullable=False)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	@classmethod
	def get(cls: SelfTicketHistoryType, ticket_history_type_id: int) -> SelfTicketHistoryType:
		"""Obtener la historia del tipo del estado del ticket por su ID
		
		Parameters
		----------
		ticket_type_id: int
			ID del ticket_type_id
		
		Returns
		-------
		TicketHistoryType
			Un objeto del tipo TicketHistoryType
		"""
		return db.session.query(cls).get(ticket_history_type_id)
	
	@classmethod
	def all(cls: SelfTicketHistoryType) -> List[SelfTicketHistoryType]:
		"""Obtener todas las historias de los tipos de los estados del ticket
	
		Returns
		-------
		List[TicketHistoryType]
			Una lista de objetos TicketHistoryType
		"""
		return db.session.query(cls).all()
