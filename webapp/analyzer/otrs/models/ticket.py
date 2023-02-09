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
			cls.ticket_state_id!=9,
			cls.customer_id.not_ilike("%@%"),
			cls.queue_id==queue_id,
			cls.title.not_ilike("%[RRD]%"),
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
				cls.ticket_state_id!=9,
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
		que sea:
		*del usuario Auto Ofensa user_id = 35
		que no sea:
		*de la cola queue_id=8 "eliminar"
		*del estado merged ticket_state_id=9

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
			cls.user_id==35,
			cls.ticket_state_id!=9,
			cls.queue_id!=8,
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
		desde un determinado id, con la palabra "Ofense  Nº" en el titulo
		que sea:
		*del usuario Auto Ofensa user_id = 35
		que no sea:
		*de la cola queue_id=8 "eliminar"
		*del estado merged ticket_state_id=9

		
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
				cls.user_id==35,
				cls.ticket_state_id!=9,
				cls.id>last_ticket_id,
				cls.queue_id!=8,
				cls.title.ilike("%Ofensa Nº%"),
				cls.create_time>=f"{start_period}",
				cls.create_time<f"{end_period}").all()

	@classmethod
	def last_ticket_id_offense_automatic_intervention_manual(cls: SelfTicket, 
			start_period: str, 
			end_period: str) -> int:
		"""Obtener el ultimo id del ticket que tenga en el titulo "Ofensa Nº"
		que sea:
		*creado por la Auto Ofensa user_id=35
		que no sea:
		*del usuario Auto Ofensa user_id = 35
		*de la cola queue_id=8 "eliminar"
		*del estado merged ticket_state_id=9

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
			cls.user_id!=35,
			cls.responsible_user_id==35,
			cls.ticket_state_id!=9,
			cls.queue_id!=8,
			cls.title.ilike("%Ofensa Nº%"),
			cls.create_time>=f"{start_period}",
			cls.create_time<f"{end_period}").order_by(desc(cls.create_time)).first()
		
		return ticket.id if ticket else 0
	

	@classmethod
	def tickets_offenses_automatic_intervention_manual_by_period(cls: SelfTicket, 
			last_ticket_id: int,
			start_period: str, 
			end_period: str) -> List[SelfTicket]:
		"""Obtener los tickets automaticos de un determinado periodo, 
		desde un determinado id, con la palabra "Ofense  Nº" en el titulo
		que sea:
		*creado por la Auto Ofensa user_id=35
		que no sea:
		*del usuario Auto Ofensa user_id = 35
		*de la cola queue_id=8 "eliminar"
		*del estado merged ticket_state_id=9
		
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
				cls.user_id!=35,
				cls.responsible_user_id==35,
				cls.ticket_state_id!=9,
				cls.id>last_ticket_id,
				cls.queue_id!=8,
				cls.title.ilike("%Ofensa Nº%"),
				cls.create_time>=f"{start_period}",
				cls.create_time<f"{end_period}").all()
	

	@classmethod
	def last_ticket_id_offense_handwork(cls: SelfTicket, 
			start_period: str, 
			end_period: str) -> int:
		"""Obtener el ultimo id del ticket que tenga en el titulo "Ofensa" 
		pero que no sea 
		* "Ofense Nº"
		*del estado merged ticket_state_id=9
		
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
			cls.ticket_state_id!=9,
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
		"""Obtener los tickets manuales de un determinado periodo, con la palabra "Ofensa"
		pero que no sea 
		* "Ofense Nº"
		*del estado merged ticket_state_id=9
		
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
			cls.ticket_state_id!=9,
			cls.id>last_ticket_id,
			cls.title.ilike("%Ofensa%"),
			cls.title.not_ilike("%Ofensa Nº%"),
			cls.create_time>=f"{start_period}",
			cls.create_time<f"{end_period}").all()
	

	#########################################################
	########### Vista Potal de Clientes #####################
	#########################################################
	
	@classmethod
	def last_ticket_id_customer_queue_period(cls: SelfTicket, 
			queue_id: int,
			customer_id: str, 
			start_period: str,
			end_period: str) -> int:
		"""Obtener el ultimo id del ticket de un cliente.

		Parameters
		----------
		customer_id: str,
			ID del cliente
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
			cls.ticket_state_id!=9,
			cls.customer_id==customer_id,
			cls.queue_id==queue_id,
			cls.create_time>=f"{start_period} 00:00:00",
			cls.create_time<f"{end_period}"
			).order_by(desc(cls.create_time)).first()

		return ticket.id if ticket else 0
	
	@classmethod
	def first_ticket_id_customer_(cls: SelfTicket, 
			queue_id: int,
			customer_id: str) -> int:
		"""Obtener el primer ticket de un cliente.
		*Con filtro de queue_id=6, solo administrativos.
		*ticket_state_id!=9 significa que que eliminan lo ticktes 
		con estado "merged".

		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente

		Returns
		-------
		El ID del primer ticket
			Un int
		"""

		ticket: SelfTicket = db.session.query(cls).filter(
			cls.ticket_state_id!=9,
			cls.customer_id==customer_id,
			cls.queue_id==queue_id,
			).order_by(asc(cls.create_time)
	    ).first()

		return ticket.id if ticket else 0
	
	
	@classmethod
	def last_ticket_id_customer_(cls: SelfTicket, 
			queue_id: int,
			customer_id: str) -> int:
		"""Obtener el ultimo ticket de un periodo
		con lo filtros de cola y cliente.
		* ticket_state_id!=9 significa que que eliminan lo ticktes 
		con merged.

		Parameters
		----------
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente

		Returns
		-------
		El ID del ultimo ticket
			Un int
		"""

		ticket: SelfTicket = db.session.query(cls).filter(
			cls.ticket_state_id!=9,
			cls.customer_id==customer_id,
			cls.queue_id==queue_id,
			).order_by(desc(cls.create_time)
	    ).first()

		return ticket.id if ticket else 0
	
	@staticmethod
	def get_by_id_customer_filtered(
		last_ticket_id: int,
		queue_id: int,
		customer_id: str, 
		start_period: str, 
		end_period: str) -> list:
		"""Obtener los tickets menores a la fecha 2023-2-7
		mayores a un id.
		"""

		start_period_ = datetime.strptime(start_period, "%Y-%m-%d")
		end_period_ = datetime.strptime(end_period, "%Y-%m-%d")
		limit_date_ = datetime.strptime("2023-2-7", "%Y-%m-%d")

		if start_period_ > limit_date_:
			return []

		if end_period_ > limit_date_:
			end_period = "2023-2-7"
		
	
		return db.session.query(Ticket).filter(
			Ticket.id>last_ticket_id,
			Ticket.ticket_state_id!=9,
			Ticket.customer_id==customer_id,
			Ticket.title.not_ilike("%[RRD]%"),
			Ticket.queue_id==queue_id,
			Ticket.create_time>=f"{start_period} 00:00:00",
			Ticket.create_time<=f"{end_period} 23:59:59"
		).all()
	

	@staticmethod
	def get_by_id_customer_(
		last_ticket_id: int,
		queue_id: int,
		customer_id: str, 
		start_period: str, 
		end_period: str) -> list:
		"""Obtener los tickets mayores a la fecha 2023-2-7
		mayores a un id.
		"""

		start_period_ = datetime.strptime(start_period, "%Y-%m-%d")
		end_period_ = datetime.strptime(end_period, "%Y-%m-%d")
		start_time_ = datetime.strptime("2023-2-7", "%Y-%m-%d")

		if end_period_ < start_time_:
			return []

		if start_period_ < start_time_:
			start_period = "2023-2-7"
	
		return db.session.query(Ticket).filter(
			Ticket.id>last_ticket_id,
			Ticket.ticket_state_id!=9,
			Ticket.customer_id==customer_id,
			Ticket.queue_id==queue_id,
			Ticket.create_time>=f"{start_period} 00:00:00",
			Ticket.create_time<=f"{end_period} 23:59:59"
		).all()


	@classmethod
	def tickets_by_id_customer(cls: SelfTicket,
			last_ticket_id: int,
			queue_id: int,
			customer_id: str, 
			start_period: str, 
			end_period: str) -> List[SelfTicket]:
		"""Obtener los tickets de los requerimientos pedidos
		por un determiando cliente en un determinado periodo
		y con id mayor al definido.
		* ticket_state_id!=9 significa que que eliminan lo ticktes 
		con merged.
		*El 7/02/2023 se creo el servicio para los tickets RRD
		por lo tanto los tickets que en el titulo tuvieran ese asunto
		antes de la fecha debian ser eliminados, dado que estaban 
		asociados solo a Adaptive Securitys

		Parameters
		----------
		last_ticket_id: int
			ID del que se quiere partir
		queue_id: int
			ID de la cola
		customer_id: str
        	ID del cliente
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		tickets = []

		tickets.extend(
			cls.get_by_id_customer_filtered(
				last_ticket_id=last_ticket_id,
				queue_id=queue_id,
				customer_id=customer_id,
				start_period=start_period,
				end_period=end_period
			)
		)
		
		tickets.extend(
			cls.get_by_id_customer_(
				last_ticket_id=last_ticket_id,
				queue_id=queue_id,
				customer_id=customer_id,
				start_period=start_period,
				end_period=end_period
			)
		)

		return tickets


	#########################################################
	########### Query para Potal de Clientes ################
	#########################################################
	
	@classmethod
	def first_ticket_customer_(cls: SelfTicket, 
			queue_id: int,
			customer_id: str) -> SelfTicket:
		"""Obtener el primer ticket de un cliente.
		*Con filtro de queue_id=6, solo administrativos.
		*ticket_state_id!=9 significa que que eliminan lo ticktes 
		con estado "merged".

		QUERY EN SQL

		USE otrs;
		SELECT *
		FROM ticket AS t
		WHERE t.ticket_state_id !=9 
		AND t.queue_id = queue_id ->6
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

		return db.session.query(cls).filter(
			cls.ticket_state_id!=9,
			cls.customer_id==customer_id,
			cls.queue_id==queue_id,
			).order_by(asc(cls.create_time)
	    ).first()

	
	@staticmethod
	def get_by_customer_filtered(
		queue_id: int,
		customer_id: str, 
		start_period: str, 
		end_period: str) -> list:
		"""Obtener los tickets menores a la fecha 2023-2-7
		
		QUERY EN SQL

		USE otrs;
		SELECT *
		FROM ticket AS t
		WHERE t.ticket_state_id !=9 
		AND t.queue_id = queue_id
		AND t.customer_id = customer_id
		AND t.create_time >= start_period
		AND t.create_time <= end_period
		AND t.title NOT LIKE "%[RRD]%
		"""

		start_period_ = datetime.strptime(start_period, "%Y-%m-%d")
		end_period_ = datetime.strptime(end_period, "%Y-%m-%d")
		limit_date_ = datetime.strptime("2023-2-7", "%Y-%m-%d")

		if start_period_ > limit_date_:
			return []

		if end_period_ > limit_date_:
			end_period = "2023-2-7"
	
		return db.session.query(Ticket).filter(
			Ticket.ticket_state_id!=9,
			Ticket.customer_id==customer_id,
			Ticket.title.not_ilike("%[RRD]%"),
			Ticket.queue_id==queue_id,
			Ticket.create_time>=f"{start_period} 00:00:00",
			Ticket.create_time<=f"{end_period} 23:59:59"
		).all()
	

	@staticmethod
	def get_by_customer_(
		queue_id: int,
		customer_id: str, 
		start_period: str, 
		end_period: str) -> list:
		"""Obtener los tickets mayores a la fecha 2023-2-7
		
		QUERY EN SQL

		USE otrs;
		SELECT *
		FROM ticket AS t
		WHERE t.ticket_state_id !=9 
		AND t.queue_id = queue_id
		AND t.customer_id = customer_id
		AND t.create_time >= start_period
		AND t.create_time <= end_period
		"""

		start_period_ = datetime.strptime(start_period, "%Y-%m-%d")
		end_period_ = datetime.strptime(end_period, "%Y-%m-%d")
		start_time_ = datetime.strptime("2023-2-7", "%Y-%m-%d")

		if end_period_ < start_time_:
			return []

		if start_period_ < start_time_:
			start_period = "2023-2-7"
	
		return db.session.query(Ticket).filter(
			Ticket.ticket_state_id!=9,
			Ticket.customer_id==customer_id,
			Ticket.queue_id==queue_id,
			Ticket.create_time>=f"{start_period} 00:00:00",
			Ticket.create_time<=f"{end_period} 23:59:59"
		).all()


	@classmethod
	def tickets_by_customer(cls: SelfTicket,
			queue_id: int,
			customer_id: str, 
			start_period: str, 
			end_period: str) -> List[SelfTicket]:
		"""Obtener los tickets de los requerimientos pedidos
		por un determiando cliente en un determinado periodo.
		* ticket_state_id!=9 significa que que eliminan lo ticktes 
		con merged.
		*El 7/02/2023 se creo el servicio para los tickets RRD
		por lo tanto los tickets que en el titulo tuvieran ese asunto
		antes de la fecha debian ser eliminados, dado que estaban 
		asociados solo a Adaptive Securitys

		QUERY EN SQL

		Es la unión de las dos anteriores.

		Parameters
		----------
		queue_id: int
			ID de la cola "6" admin
		customer_id: str
        	ID del cliente
		start_period: str
			Fecha inicio en formato Y-M-D
		end_period: str
			Fecha fin en formato Y-M-D
		
		Returns
		-------
		list[Ticket]
			Una lista de objetos Ticket
		"""

		tickets = []

		tickets.extend(
			cls.get_by_customer_filtered(
				queue_id=queue_id,
				customer_id=customer_id,
				start_period=start_period,
				end_period=end_period
			)
		)

		tickets.extend(
			cls.get_by_customer_(
				queue_id=queue_id,
				customer_id=customer_id,
				start_period=start_period,
				end_period=end_period
			)
		)

		return tickets