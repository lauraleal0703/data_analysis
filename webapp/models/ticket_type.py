from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from webapp.models import db


SelfTicketType = TypeVar("SelfTicketType", bound="TicketType")

class TicketType(db.Model):
	__tablename__ = 'ticket_type'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	valid_id = Column(Integer, nullable=False)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	@classmethod
	def get(cls: SelfTicketType, ticket_type_id: int) -> SelfTicketType:
		"""Obtener el tipo del estado del ticket por su ID
		
		Parameters
		----------
		ticket_type_id: int
			ID del ticket_type_id
		
		Returns
		-------
		TicketType
			Un objeto del tipo TicketType
		"""
		return db.session.query(cls).get(ticket_type_id)
	
	@classmethod
	def all(cls: SelfTicketType) -> List[SelfTicketType]:
		"""Obtener todos los typos de los estados del ticket
	
		Returns
		-------
		List[SelfTicketType]
			Una lista de objetos SelfTicketType
		"""
		return db.session.query(cls).all()

