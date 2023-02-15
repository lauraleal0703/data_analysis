from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from typing import TypeVar, List

from . import db
from .ticket_history_type import TicketHistoryType
from .ticket_type import TicketType
from .ticket_priority import TicketPriority
from .ticket_state import TicketState


SelfTicketHistory = TypeVar("SelfTicketHistory", bound="TicketHistory")

class TicketHistory(db.Base):
	__tablename__ = 'ticket_history'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	history_type_id = Column(Integer, ForeignKey("ticket_history_type.id"), nullable=False)
	ticket_id = Column(Integer, ForeignKey("ticket.id"), nullable=False)
	article_id = Column(Integer, nullable=True)
	type_id = Column(Integer, ForeignKey("ticket_type.id"), nullable=False)
	queue_id = Column(Integer, nullable=False)
	owner_id = Column(Integer, nullable=False)
	priority_id = Column(Integer, ForeignKey("ticket_priority.id"), nullable=False)
	state_id = Column(Integer, ForeignKey("ticket_state.id"), nullable=False)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	ticket = relationship("Ticket", back_populates="ticket_history", lazy=True)
	priority: TicketPriority = relationship("TicketPriority", lazy=True)
	ticket_state: TicketState = relationship("TicketState", lazy=True)
	ticket_type: TicketType = relationship("TicketType", lazy=True)
	ticket_history_type: TicketHistoryType = relationship("TicketHistoryType", lazy=True)


	@classmethod
	def get(cls: SelfTicketHistory, ticket_id: int) -> List[SelfTicketHistory]:
		"""Obtener el historial de un ticket por su ID
		
		Parameters
		----------
		ticket_id: int
			ID del ticket
		
		Returns
		-------
		List[TicketHistory]
			Un lista con objetos del tipo TicketHistory
		"""
		return db.session.query(cls).filter(cls.ticket_id == ticket_id).all()
