from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy import and_
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
	

	########################################
	#############QUERY#####################
	#######################################
	

	@classmethod
	def first_ticket_customer(cls: SelfTicket, 
			queue_id: int,
			customer_id: str) -> SelfTicket:
		"""Obtener el primer ticket de un cliente.
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
		ORDER BY t.create_time ASC LIMIT 1

		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente

		Returns
		-------
		El primer ticket
			Un objeto ticket
		"""

		exceptions_type = [68]
		exceptions_state = [5, 9, 15]

		return db.session.query(cls).filter(
			cls.type_id.notin_(exceptions_type),
			cls.ticket_state_id.notin_(exceptions_state),
			cls.customer_id == customer_id,
			cls.queue_id == queue_id,
			).order_by(asc(cls.create_time)
	    ).first()
	

	@classmethod
	def last_ticket_customer(cls: SelfTicket, 
			queue_id: int,
			customer_id: str) -> SelfTicket:
		"""Obtener el último ticket de un cliente.
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
		ORDER BY t.create_time DESC LIMIT 1

		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente

		Returns
		-------
		El último ticket
			Un objeto ticket
		"""
		exceptions_type = [68]
		exceptions_state = [5, 9, 15]

		return db.session.query(cls).filter(
			cls.type_id.notin_(exceptions_type),
			cls.ticket_state_id.notin_(exceptions_state),
			cls.customer_id == customer_id,
			cls.queue_id == queue_id,
			).order_by(desc(cls.create_time)
	    ).first()


	@classmethod
	def ticktets_filtered_with(cls: SelfTicket,
		start_period: str,
		end_period: str,
		queue_id: Optional[int] = None,
		user_id: Optional[int] = None,
		customer_id: Optional[str] = None
	) -> List[SelfTicket]:
		"""Obtener los tickests de un periodo dado los filtros
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
		AND t.create_time >= "start_period 00:00:00"
		AND t.create_time >= "end_period 23:59:59"

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
		List
			Una lista de objetos de tipo ticket
		"""
		exceptions_type = [68]
		exceptions_state = [5, 9, 15]
		
		query = db.session.query(cls).filter(
			cls.type_id.notin_(exceptions_type),
			cls.ticket_state_id.notin_(exceptions_state),
			cls.create_time >= f"{start_period} 00:00:00",
			cls.create_time <= f"{end_period} 23:59:59"
		)

		if queue_id:
			query = query.filter(cls.queue_id == queue_id)
		
		if customer_id:
			query = query.filter(cls.customer_id == customer_id)
		
		if user_id:
			query = query.filter(cls.user_id == user_id)

		tickets: List[SelfTicket] = query.all()

		return tickets
	
	#########################################################################