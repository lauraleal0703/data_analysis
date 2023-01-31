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
	def last_ticket(cls: SelfTicket) -> SelfTicket:
		"""Obtener el ultimo ticket.
	
		Returns
		-------
		Ticket
			Un objeto de typo Ticket
		"""

		return db.session.query(cls).order_by(desc(cls.create_time)).first()
	
	@classmethod
	def last_ticket_offense(cls: SelfTicket) -> SelfTicket:
		"""Obtener el ultimo ticket que tenga en el titulo "Ofensa"
	
		Returns
		-------
		Ticket
			Un objeto de typo Ticket
		"""

		return db.session.query(cls).filter(cls.title.ilike("%Ofensa%")).order_by(desc(cls.create_time)).first()
	
	@classmethod
	def last_ticket_queue(cls: SelfTicket, queue_id:int) -> SelfTicket:
		"""Obtener el ultimo ticket.

		Parameters
		----------
		queue_id: int
			ID de la cola

		Returns
		-------
		Ticket
			Un objeto de typo Ticket
		"""

		return db.session.query(cls).filter(cls.queue_id==queue_id).order_by(desc(cls.create_time)).first()
	
	
	@classmethod
	def tickets_by_queue_period(cls: SelfTicket, queue_id:int, start_period: str, end_period: str) -> List[SelfTicket]:
		"""Obtener los ticket de un determinado periodo, con queue_id.
		
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
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.queue_id==queue_id,
				cls.create_time>=f"{start_period}",
				cls.create_time<f"{end_period}").all()
	
	@classmethod
	def tickets_offenses_by_period(cls: SelfTicket, start_period: str, end_period: str) -> List[SelfTicket]:
		"""Obtener los ticket de un determinado periodo, con la palabra "Ofense" en el titulo.
		
		Parameters
		----------
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
				cls.title.ilike("%Ofensa%"),
				cls.create_time>=f"{start_period}",
				cls.create_time<f"{end_period}").all()

	@classmethod
	def tickets_by_date(cls: SelfTicket, date: str) -> List[SelfTicket]:
		"""Obtener los ticket de una determinada fecha.
		
		Parameters
		----------
		date: str
			Fecha  en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.create_time>=f"{date} 00:00:00",
				cls.create_time<=f"{date} 23:59:59").all()
	
	@classmethod
	def tickets_by_customer_date(cls: SelfTicket, customer_id: str, date: str) -> List[SelfTicket]:
		"""Obtener los tickets diarios generados por un cliente.
		
		Parameters
		----------
		customer_id: str
			ID del customer.
		date: str
			Fecha del día en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.customer_id == customer_id,
				cls.create_time>=f"{date} 00:00:00",
				cls.create_time<=f"{date} 23:59:59").all()
	
	@classmethod
	def tickets_by_customer_date_queue(cls: SelfTicket, queue_id: int, customer_id: str, date: str) -> List[SelfTicket]:
		"""Obtener los tickets diarios generados por un cliente.
			Dado un ID de cola
		
		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
			ID del customer.
		date: str
			Fecha del día en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.queue_id == queue_id,
				cls.customer_id == customer_id,
				cls.create_time >= f"{date} 00:00:00",
				cls.create_time <= f"{date} 23:59:59").all()
	
	@classmethod
	def tickets_by_customer_service_date_queue(cls: SelfTicket, queue_id: int, customer_id: str, service_id:int, last_id:int, date: str) -> List[SelfTicket]:
		"""Obtener los tickets diarios generados por un cliente.
			Dado un ID de inicio y eñ id de la cola
		
		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
			ID del customer.
		service_id: str
			ID del service.
		las_id: int
			ID desde el cual se quiere buscar
		date: str
			Fecha del día en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.id>last_id,
				cls.service_id==service_id,
				cls.queue_id==queue_id,
				cls.customer_id==customer_id,
				cls.create_time>=f"{date} 00:00:00",
				cls.create_time<=f"{date} 23:59:59").all()
	
	@classmethod
	def tickets_by_queue_user_date(cls: SelfTicket, queue_id: int, user_id: int, last_id:int, date: str) -> List[SelfTicket]:
		"""Obtener los ticket de una cola en determinada fecha.
		
		Parameters
		----------
		user_id: int
			ID del usuario.
		queue_id: int
			ID de la cola.
		las_id: int
			ID desde el cual se quiere buscar.
		date: str
			Fecha en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.id>last_id,
				cls.user_id == user_id,
				cls.queue_id == queue_id,
                cls.create_time>=f"{date} 00:00:00",
                cls.create_time<f"{date} 23:59:59").all()
	
	@classmethod
	def tickets_by_queue_user_date_customer_service(cls: SelfTicket, queue_id: int, user_id: int, customer_id: str, service_id:int, last_id:int, date: str) -> List[SelfTicket]:
		"""Obtener los ticket de una cola en determinada fecha.
		
		Parameters
		----------
		user_id: int
			ID del usuario.
		queue_id: int
			ID de la cola.
		customer_id: str
			ID del customer.
		service_id: str
			ID del service.
		las_id: int
			ID desde el cual se quiere buscar.
		date: str
			Fecha en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.id>last_id,
				cls.service_id==service_id,
				cls.user_id == user_id,
				cls.queue_id == queue_id,
				cls.customer_id == customer_id,
                cls.create_time>=f"{date} 00:00:00",
                cls.create_time<f"{date} 23:59:59").all()
	
	
	@classmethod
	def tickets_by_customer(cls: SelfTicket, customer_id: str) -> List[SelfTicket]:
		"""Obtener los ticket de un cliente.
		
		Parameters
		----------
		customer_id: str
			ID del customer.
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		return db.session.query(cls).filter(
				cls.customer_id == customer_id).all()
	
	@classmethod
	def last_ticket_customer(cls: SelfTicket, customer_id: str) -> SelfTicket:
		"""Obtener el ultimo ticket del cliente .
		
		Parameters
		----------
		customer_id: str
			ID del customer.
		
		Returns
		-------
		Ticket
			Una objeto Ticket
		"""

		return db.session.query(cls).filter(cls.customer_id == customer_id).order_by(desc(cls.create_time)).first()

	@classmethod
	def tickets_by_marca_in_title(cls: SelfTicket, marca=str) -> SelfTicket:
		"""Obtener los tickets asociados al id de una ofensa de QRadar
		
		Parameters
		---------
		offense_id: str
			ID de la ofensa en QRadar
			
		Returns
		-------
		list[Ticket]
			Una lista de objetos tipo ticket
		"""
		return db.session.query(cls).filter(cls.title.ilike(f"%{marca}%")).all()

	@classmethod
	def tickets_by_queue_marca_date(cls: SelfTicket, queue_id: int, marca: str, start_date: str, end_date: str=None) -> List[SelfTicket]:
		"""Obtener los ticket de una cola en determinada fecha.
		
		Parameters
		----------
		queue_id: int
			ID de la cola.
		marca: str
			Frase referencial que este en el titulo.
		start_date: str
			Fecha de inicio en formato Y-M-D
		end_date: str
			Fecha de fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""
		if not end_date:
			end_date = datetime.today().strftime("%Y-%m-%d")

		return db.session.query(cls).filter(
				cls.queue_id == queue_id,
				cls.title.ilike(f"%{marca}%"),
                cls.create_time>=f"{start_date} 00:00:00",
                cls.create_time<f"{end_date} 23:00:00").all()
	
	@classmethod
	def tickets_by_queue_date(cls: SelfTicket, queue_id: int, start_date: str, end_date: str=None) -> List[SelfTicket]:
		"""Obtener los ticket de una cola en determinada fecha.
		
		Parameters
		----------
		queue_id: int
			ID de la cola.
		start_date: str
			Fecha de inicio en formato Y-M-D
		end_date: str
			Fecha de fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""
		if not end_date:
			end_date = datetime.today().strftime("%Y-%m-%d")

		return db.session.query(cls).filter(
				cls.queue_id == queue_id,
                cls.create_time>=f"{start_date} 00:00:00",
                cls.create_time<f"{end_date} 23:00:00").all()
		
	
		
	@classmethod
	def tickets_by_user_date(cls: SelfTicket, user_id: int, start_date: str, end_date: str=None) -> List[SelfTicket]:
		"""Obtener los ticket de un usuario en determinada fecha.
		
		Parameters
		----------
		user_id: int
			ID del usuario.
		start_date: str
			Fecha de inicio en formato Y-M-D
		end_date: str
			Fecha de fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""
		if not end_date:
			end_date = datetime.today().strftime("%Y-%m-%d")

		return db.session.query(cls).filter(
				cls.user_id == user_id,
                cls.create_time>=f"{start_date} 00:00:00",
                cls.create_time<f"{end_date} 23:00:00").all()
		
	@classmethod
	def tickets_by_dates(cls: SelfTicket, start_date: str, end_date: str=None) -> List[SelfTicket]:
		"""Obtener los ticket de una cola en determinada fecha.
		
		Parameters
		----------
		start_date: str
			Fecha de inicio en formato Y-M-D
		end_date: str
			Fecha de fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""
		if not end_date:
			end_date = datetime.today().strftime("%Y-%m-%d")

		return db.session.query(cls).filter(
				cls.create_time>=f"{start_date} 00:00:00",
				cls.create_time<f"{end_date} 23:00:00").all()
