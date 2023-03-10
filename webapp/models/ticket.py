from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import desc
from sqlalchemy import asc
from sqlalchemy.orm import relationship


from datetime import datetime
from datetime import timedelta

from typing import TypeVar
from typing import List
from typing import Optional
from typing import Union

from webapp.models import db
from webapp.models.ticket_type import TicketType
from webapp.models.service import Service
from webapp.models.sla import Sla
from webapp.models.user import User
from webapp.models.ticket_priority import TicketPriority
from webapp.models.ticket_state import TicketState
from webapp.models.queue import Queue
from webapp.models.ticket_history import TicketHistory
from webapp.models.customer_company import CustomerCompany
from webapp.models.dynamic_field_value import DynamicFieldValue

from webapp.analyzer.qradar import qradar


import logging
logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
        level=logging.DEBUG
    )


SelfTicket = TypeVar("SelfTicket", bound="Ticket")

class Ticket(db.Model):
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
	def service_id(self: SelfTicket):
		"""JAM??S CAMBIAR O EL NONE DA PROBLEMAS EN LA B??SQUEDA"""
		if self._service_id is None:
			return "Undefined"
		return self._service_id

	@property
	def last_history(self: SelfTicket) -> TicketHistory:
		""""Obtener el ??ltimo registro del historial de un ticket
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
	

	def tojson_(self: SelfTicket) -> dict:
		
		qradar_id = DynamicFieldValue.get_offense_id(self.id)
		qradar_time_format = ""
		response_time_format = ""
		if qradar_id:
			qradar_time = qradar.start_time_offense(qradar_id)
			if qradar_time:
				response_time = (self.create_time + timedelta(hours=1)) - qradar_time
				response_time_format = str(response_time)
				logging.debug(f"response_time_format {response_time_format}")
				qradar_time_format = qradar_time.strftime("%d-%m-%Y %H:%M:%S")
		else:
			qradar_time = "Sin Informaci??n"
		
		dicy_ticket = {
			"id": self.id,
			"tn": self.tn,
			"create_time": self.create_time.strftime("%d-%m-%Y %H:%M:%S"),
			"title": self.title,
			"type.name": self.type.name if self.type else self.type_id,
			"user.full_name": self.user.full_name,
			"service.name": self.service.name if self.service else self.service_id,
			"customer_id": self.customer_id,
			"ticket_state.name": self.ticket_state.name if self.ticket_state else self.ticket_state_id,
			"ticket_priority.name": self.ticket_priority.name if self.ticket_priority else self.ticket_priority_id,
			"queue_id": self.queue_id,
			"qradar_id": qradar_id if qradar_id else "Sin Informaci??n",
			"qradar_time": qradar_time_format if qradar_time_format else "Sin Informaci??n",
			"response_time": response_time_format if response_time_format else "Sin Informaci??n"
		}

		return dicy_ticket
	
	def tojson(self: SelfTicket) -> dict:
		
		qradar_id = ""
		qradar_time_format = ""
		response_time = ""
		
		dicy_ticket = {
			"id": self.id,
			"tn": self.tn,
			"create_time": self.create_time.strftime("%d-%m-%Y %H:%M:%S"),
			"title": self.title,
			"type.name": self.type.name if self.type else self.type_id,
			"user.full_name": self.user.full_name,
			"service.name": self.service.name if self.service else self.service_id,
			"customer_id": self.customer_id,
			"ticket_state.name": self.ticket_state.name if self.ticket_state else self.ticket_state_id,
			"ticket_priority.name": self.ticket_priority.name if self.ticket_priority else self.ticket_priority_id,
			"queue_id": self.queue_id,
			"qradar_id": qradar_id if qradar_id else "Sin Informaci??n",
			"qradar_time": qradar_time_format if qradar_time_format else "Sin Informaci??n",
			"response_time": response_time if response_time else "Sin Informaci??n"
		}

		return dicy_ticket

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
		customers: Optional[list] = None,
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
		AND t.create_time < "end_period 00:00:00"

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
		
		if customers:
			query = query.filter(cls.customer_id.in_(customers))
		
		if user_id:
			query = query.filter(cls.user_id == user_id)
		
		if count:
			return query.count()

		return query.all()
	

	@classmethod
	def tickets_conflict(cls: SelfTicket,
		time: str,
		queue_id: int,
		users_id: list,
		customers: list
	) -> List[SelfTicket]:
		"""Obtener los tickests como una lista de objetos
		de un periodo dado los filtros
		*type_id = 68 es Accion preventiva
		*ticket_state_id = 5 es removed
		*ticket_state_id = 9 es merged
		*ticket_state_id = 15 es cancelado
		
		QUERY EN SQL

		SELECT *
		FROM ticket AS t
		WHERE t.type_id NOT IN (68)
		AND t.ticket_state_id NOT IN (5, 9, 15) 
		AND t.queue_id = queue_id
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
		users_id = users_id + [1]

		if time == "month":
			start_period = datetime.strftime(datetime.today() - timedelta(days=7), "%Y-%m-%d")
			end_period = datetime.strftime(datetime.today() + timedelta(days=1), "%Y-%m-%d")
		if time == "year":
			start_period = "2022-01-01"
			end_period = "2023-01-01"
		if time == "twoYear":
			start_period = "2021-01-01"
			end_period = "2022-01-01"

		query = db.session.query(cls).filter(
			cls.create_time >= f"{start_period} 00:00:00",
			cls.create_time < f"{end_period} 00:00:00",
			cls.queue_id == queue_id,
			cls.user_id.notin_(users_id),
			cls.customer_id.in_(customers),
			cls.type_id.notin_(exceptions_type),
			cls.ticket_state_id.notin_(exceptions_state),
			cls._service_id.is_(None)
		)

		return query.all()
