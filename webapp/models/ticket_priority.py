from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from webapp.models import db

SelfTicketPriority = TypeVar("SelfTicketPriority", bound="TicketPriority")

class TicketPriority(db.Model):
	__tablename__ = 'ticket_priority'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	valid_id = Column(Integer, nullable=False)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	@classmethod
	def get(cls: SelfTicketPriority, ticket_priority_id: int) -> SelfTicketPriority:
		"""Obtener la prioridad del ticket por su ID
		
		Parameters
		----------
		ticket_priority_id: int
			ID del ticket_priority
		
		Returns
		-------
		TicketPriority
			Un objeto del tipo TicketPriority
		"""
		return db.session.query(cls).get(ticket_priority_id)
	
	@classmethod
	def all(cls: SelfTicketPriority) -> List[SelfTicketPriority]:
		"""Obtener todos las prioridades del ticket
	
		Returns
		-------
		List[SelfTicketPriority]
			Una lista de objetos TicketPriority
		"""
		return db.session.query(cls).all()

