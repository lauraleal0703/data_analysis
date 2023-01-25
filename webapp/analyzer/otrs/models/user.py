from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

from typing import TypeVar, List

from . import db

SelfUser = TypeVar("SelfUser", bound="User")

class User(db.Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	login = Column(String, nullable=False)
	pw = Column(String, nullable=False)
	title = Column(String, nullable=True)
	first_name = Column(String, nullable=False)
	last_name = Column(String, nullable=False)
	valid_id = Column(Integer, nullable=False)
	create_time = Column(DateTime, nullable=False)
	create_by = Column(Integer, nullable=False)
	change_time = Column(DateTime, nullable=False)
	change_by = Column(Integer, nullable=False)

	tickets = relationship("Ticket", back_populates="user", lazy=True)

	@classmethod
	def get(cls: SelfUser, user_id: int) -> SelfUser:
		"""Obtener un usuario por su ID
		
		Parameters
		----------
		user_id: int
			ID del usuario
		
		Returns
		-------
		User
			Un objeto del tipo User
		"""
		return db.session.query(cls).get(user_id)
	
	@classmethod
	def all(cls: SelfUser) -> List[SelfUser]:
		"""Obtener todos los usuarios
	
		Returns
		-------
		List[User]
			Una lista de objetos User
		"""
		return db.session.query(cls).all()

	@property
	def full_name(self):
		return f"{self.first_name} {self.last_name}"

