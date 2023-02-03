from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import desc
from sqlalchemy.orm import relationship

from typing import TypeVar, List
from typing import Union

from . import db
from .ticket_type import TicketType
from .service import Service
from .sla import Sla
from .user import User
from .ticket_priority import TicketPriority
from .ticket_state import TicketState
from .queue import Queue
from .ticket_history import TicketHistory


SelfTicket = TypeVar("SelfTicket", bound="Ticket")

class Ticket(db.Base):
	__tablename__ = 'ticket'
	id = Column(Integer, primary_key=True)
	tn = Column(String, nullable=False)
	title = Column(String, nullable=True)
	queue_id = Column(Integer, ForeignKey("queue.id"), nullable=False)
	ticket_lock_id = Column(Integer, nullable=False)
	_type_id = Column("type_id",Integer, ForeignKey("ticket_type.id"), nullable=True)
	_service_id = Column("service_id", Integer, ForeignKey("service.id"), nullable=True)
	_sla_id = Column("sla_id", Integer, ForeignKey("sla.id"), nullable=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	responsible_user_id = Column(Integer, nullable=False)
	ticket_priority_id = Column(Integer, ForeignKey("ticket_priority.id"), nullable=False)
	ticket_state_id = Column(Integer, ForeignKey("ticket_state.id"), nullable=False)
	customer_id = Column(String, nullable=True)
	customer_user_id = Column(String, nullable=True)
	timeout = Column(Integer, nullable=False)
	until_time = Column(Integer, nullable=False)
	escalation_time = Column(Integer, nullable=False)
	escalation_update_time = Column(Integer, nullable=False)
	escalation_response_time = Column(Integer, nullable=False)
	escalation_solution_time = Column(Integer, nullable=False)
	archive_flag = Column(Integer, default=0)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	queue: Queue = relationship("Queue", lazy=True)
	type: TicketType = relationship("TicketType", lazy=True)
	service: Service = relationship("Service", lazy=True)
	sla: Sla = relationship("Sla", lazy=True)
	user: User = relationship("User", back_populates="tickets", lazy=True)
	ticket_priority: TicketPriority = relationship("TicketPriority", lazy=True)
	ticket_state: TicketState = relationship("TicketState", lazy=True)
	ticket_history: TicketHistory = relationship("TicketHistory", back_populates="ticket", lazy=True)
	
	@property
	def service_id(self: SelfTicket) -> Union[int, str]:
		"""Redefinir la variable en caso de que sea NULL"""
		if not self._service_id:
			return "Undefined"
		return self._service_id

	@property
	def sla_id(self: SelfTicket)  -> Union[int, str]:
		"""Redefinir la variable en caso de que sea NULL"""
		if not self._sla_id:
			return "Undefined"
		return self._sla_id
	
	@property
	def type_id(self: SelfTicket)  -> Union[int, str]:
		"""Redefinir la variable en caso de que sea NULL"""
		if not self._type_id:
			return "Undefined"
		return self._type_id

	@property
	def last_history(self: SelfTicket) -> TicketHistory:
		""""Obtener el último registro del historial de un ticket
		
		Returns
		-------
		TicketHistory
			Un objeto del tipo TicketHistory
		"""
		return db.session.query(TicketHistory).join(Ticket).filter(
			TicketHistory.ticket_id == self.id
		).order_by(desc(TicketHistory.change_time)).first()


	@classmethod
	def get(cls: SelfTicket, ticket_id: int) -> SelfTicket:
		"""Obtener un ticket por su ID
		
		Parameters
		----------
		ticket_id: int
			ID del ticket
		
		Returns
		-------
		Ticket
			Un objeto del tipo Ticket
		"""
		return db.session.query(cls).get(ticket_id)
	

	@classmethod
	def get_by_tn(cls: SelfTicket, tn: str) -> SelfTicket:
		"""Obtener un ticket por su tn.
		
		Parameters
		----------
		tn: str
			Número del ticket
		
		Returns
		-------
		Ticket
			Un objeto del tipo ticket
		"""
		return db.session.query(cls).filter_by(tn=tn).first()
	

	@classmethod
	def tickets_from_id(cls: SelfTicket, tickets_id: int) -> List[SelfTicket]:
		"""Obtener los tickets desde un id determinado.
		
		Parameters
		----------
		tickets_id: int
			ID del ultimo ticket
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(cls.id > tickets_id).all()
	

	@classmethod
	def last_ticket_id_queue_period(cls: SelfTicket, 
			queue_id: int, 
			start_period: str,
			end_period: str) -> int:
		"""Obtener el ultimo ticket de un periodo
		con lo filtros de cola y cliente.

		Parameters
		----------
		queue_id: int
			ID de la cola
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D

		Returns
		-------
		ID del ultimo ticket
			Un entero
		"""

		ticket: SelfTicket = db.session.query(cls).filter(
			cls.customer_id.not_ilike("%@%"),
			cls.queue_id==queue_id,
			cls.create_time>=f"{start_period}",
			cls.create_time<f"{end_period}"
			).order_by(desc(cls.create_time)).first()

		return ticket.id if ticket else 0
	
	
	@classmethod
	def tickets_by_queue_period(cls: SelfTicket, 
			last_ticket_id: int,
			queue_id: int, 
			start_period: str, 
			end_period: str) -> List[SelfTicket]:
		"""Obtener los ticket de un determinado periodo, 
		a partir de un id, con queue_id
		que no tienen customer con nombres "%@%" y en el titulo no tienen
		la frase "[RRD]".
		
		Parameters
		----------
		last_ticket_id: int:
			ID del ultimo ticket analizado
		queue_id: int
			ID de la cola
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.id>last_ticket_id,
				cls.customer_id.not_ilike("%@%"),
				cls.title.not_ilike("%[RRD]%"),
				cls.queue_id==queue_id,
				cls.create_time>=f"{start_period}",
				cls.create_time<f"{end_period}").all()
	

	@classmethod
	def last_ticket_id_offense_automatic(cls: SelfTicket, 
			start_period: str, 
			end_period: str) -> int:
		"""Obtener el ultimo id del ticket que tenga en el titulo "Ofensa Nº"

		arameters
		----------
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D

		Returns
		-------
		ID del ultimo ticket
			Un entero
		"""

		ticket: SelfTicket = db.session.query(cls).filter(
			cls.title.ilike("%Ofensa Nº%"),
			cls.create_time>=f"{start_period}",
			cls.create_time<f"{end_period}").order_by(desc(cls.create_time)).first()
		
		return ticket.id if ticket else 0
	

	@classmethod
	def tickets_offenses_automatic_by_period(cls: SelfTicket, 
			last_ticket_id: int,
			start_period: str, 
			end_period: str) -> List[SelfTicket]:
		"""Obtener los tickets automaticos de un determinado periodo, 
		desde un determinado id, con la palabra "Ofense  Nº" en el titulo.
		
		Parameters
		----------
		last_ticket_id: int:
			ID del ultimo ticket analizado
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.id>last_ticket_id,
				cls.title.ilike("%Ofensa Nº%"),
				cls.create_time>=f"{start_period}",
				cls.create_time<f"{end_period}").all()
	

	@classmethod
	def last_ticket_id_offense_handwork(cls: SelfTicket, 
			start_period: str, 
			end_period: str) -> int:
		"""Obtener el ultimo id del ticket que tenga en el titulo "Ofensa" pero no "Ofense Nº"
		
		Parameters
		----------
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D
		
		Returns
		-------
		Ticket
			Un objeto de typo Ticket
		"""
		ticket: SelfTicket = db.session.query(cls).filter(
			cls.title.ilike("%Ofensa%"),
			cls.title.not_ilike("%Ofensa Nº%"),
			cls.create_time>=f"{start_period}",
			cls.create_time<f"{end_period}").order_by(desc(cls.create_time)).first()
		
		return ticket.id if ticket else 0
	
	@classmethod
	def tickets_offenses_handwork_by_period(cls: SelfTicket, 
			last_ticket_id: int,
			start_period: str, 
			end_period: str) -> List[SelfTicket]:
		"""Obtener los tickets manuales de un determinado periodo, con la palabra "Ofensa" pero no "Ofense Nº" en el titulo.
		
		Parameters
		----------
		last_ticket_id: int:
			ID del ultimo ticket analizado
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
			cls.id>last_ticket_id,
			cls.title.ilike("%Ofensa%"),
			cls.title.not_ilike("%Ofensa Nº%"),
			cls.create_time>=f"{start_period}",
			cls.create_time<f"{end_period}").all()