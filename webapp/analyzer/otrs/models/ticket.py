from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import and_
from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy.orm import relationship


from typing import TypeVar
from typing import List
from typing import Optional
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
from .customer_company import CustomerCompany


SelfTicket = TypeVar("SelfTicket", bound="Ticket")

class Ticket(db.Base):
	__tablename__ = 'ticket'
	id = Column(Integer, primary_key=True)
	tn = Column(String, nullable=False)
	title = Column(String, nullable=True)
	queue_id = Column(Integer, ForeignKey("queue.id"), nullable=False)
	ticket_lock_id = Column(Integer, nullable=False)
	type_id = Column(Integer, ForeignKey("ticket_type.id"), nullable=True)
	_service_id = Column("service_id", Integer, ForeignKey("service.id"), nullable=True)
	sla_id = Column(Integer, ForeignKey("sla.id"), nullable=True)
	user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
	responsible_user_id = Column(Integer, nullable=False)
	ticket_priority_id = Column(Integer, ForeignKey("ticket_priority.id"), nullable=False)
	ticket_state_id = Column(Integer, ForeignKey("ticket_state.id"), nullable=False)
	customer_id = Column(String, ForeignKey("customer_company.customer_id"), nullable=True)
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
	customer: CustomerCompany = relationship("CustomerCompany", lazy=True)
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
	def last_history(self: SelfTicket) -> TicketHistory:
		""""Obtener el último registro del historial de un ticket
		con estado = 27 "StateUpdate"
		
		Returns
		-------
		TicketHistory
			Un objeto del tipo TicketHistory
		"""
		return db.session.query(TicketHistory).join(Ticket).filter(
			TicketHistory.ticket_id == self.id,
			TicketHistory.history_type_id == 27
		).order_by(desc(TicketHistory.create_time)).first()


	@property
	def historys(self: SelfTicket) -> List[TicketHistory]:
		""""Obtener el todos los registro del historial de un ticket
		con estado = 27 "StateUpdate"
		
		Returns
		-------
		TicketHistory
			Un objeto del tipo TicketHistory
		"""
		return db.session.query(TicketHistory).join(Ticket).filter(
			TicketHistory.ticket_id == self.id,
			TicketHistory.history_type_id == 27
		).order_by(asc(TicketHistory.create_time)).all()
	

	####################################################
	#############QUERY TICKETS##########################
	###################################################
	
	@classmethod
	def tickets_filtered_with(cls: SelfTicket,
		queue_id: Optional[int] = None,
		user_id: Optional[int] = None,
		customer_id: Optional[str] = None,
		first_ticket: bool = False,
		last_ticket: bool = False
	) -> SelfTicket:
		"""Obtener todos los tickests dado los filtros
		*type_id = 68 es Accion preventiva
		*ticket_state_id = 5 es removed
		*ticket_state_id = 9 es merged
		*ticket_state_id = 15 es cancelado
		
		QUERY EN SQL

		USE otrs;
		SELECT *
		FROM ticket AS t
		WHERE t.type_id NOT IN (68)
		AND t.ticket_state_id NOT IN (5, 9, 15) 
		AND t.queue_id = queue_id
		AND t.customer_id = customer_id
		AND t.user_id = user_id

		ORDER BY t.create_time ASC LIMIT 1
		ORDER BY t.create_time DESC LIMIT 1

		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente
		user_id: str
        	ID del usuario

		Returns
		-------
		Ticket
			Un onjeto del tipo ticket
		"""
		exceptions_type = [68]
		exceptions_state = [5, 9, 15]
		
		query = db.session.query(cls).filter(
			cls.type_id.notin_(exceptions_type),
			cls.ticket_state_id.notin_(exceptions_state)
		)

		if queue_id:
			query = query.filter(cls.queue_id == queue_id)
		
		if customer_id:
			query = query.filter(cls.customer_id == customer_id)
		
		if user_id:
			query = query.filter(cls.user_id == user_id)

		if first_ticket:
			return query.order_by(asc(cls.create_time)).first()

		if last_ticket:
			return query.order_by(desc(cls.create_time)).first()
	

	@classmethod
	def tickets_period_filtered_with(cls: SelfTicket,
		start_period: str,
		end_period: str,
		queue_id: Optional[int] = None,
		user_id: Optional[int] = None,
		customer_id: Optional[str] = None,
		count: bool = False
	) -> Union[int, List[SelfTicket]]:
		"""Obtener los tickests (como una lista de objetos
		o solo la cantidad) de un periodo dado los filtros
		*type_id = 68 es Accion preventiva
		*ticket_state_id = 5 es removed
		*ticket_state_id = 9 es merged
		*ticket_state_id = 15 es cancelado
		
		QUERY EN SQL

		USE otrs;
		SELECT COUNT(t.id)

		SELECT *
		FROM ticket AS t
		WHERE t.type_id NOT IN (68)
		AND t.ticket_state_id NOT IN (5, 9, 15) 
		AND t.queue_id = queue_id
		AND t.customer_id = customer_id
		AND t.user_id = user_id
		AND t.create_time >= "start_period 00:00:00"
		AND t.create_time < "end_period 23:59:59"

		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente
		user_id: str
        	ID del usuario

		Returns
		-------
		Int
			Cantidad de tickets COUNT(*)
		List 
			Una lista de objetos de tipo ticket
		"""
		exceptions_type = [68]
		exceptions_state = [5, 9, 15]
		
		query = db.session.query(cls).filter(
			cls.type_id.notin_(exceptions_type),
			cls.ticket_state_id.notin_(exceptions_state),
			cls.create_time >= f"{start_period} 00:00:00",
			cls.create_time < f"{end_period} 00:00:00"
		)

		if queue_id:
			query = query.filter(cls.queue_id == queue_id)
		
		if customer_id:
			query = query.filter(cls.customer_id == customer_id)
		
		if user_id:
			query = query.filter(cls.user_id == user_id)
		
		if count:
			return query.count()

		return query.all()
