from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from typing import TypeVar, List

from webapp.models import db


SelfCustomerCompany = TypeVar("SelfCustomerCompany", bound="CustomerCompany")

class CustomerCompany(db.Model):
    __tablename__ = 'customer_company'
    customer_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    street = Column(String, nullable=True)
    zip = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    url = Column(String, nullable=True)
    comments = Column(String, nullable=True)
    valid_id = Column(Integer, nullable=False)
    create_time = Column(DateTime, nullable=False)
    create_by = Column(Integer, nullable=False)
    change_time = Column(DateTime, nullable=False)
    change_by = Column(Integer, nullable=False)

    @classmethod
    def get(cls: SelfCustomerCompany, customer_id: int) -> SelfCustomerCompany:
        """Obtener un customer por su ID
        
        Parameters
        ----------
        customer_id: int
            ID del customer
        
        Returns
        -------
        CustomerCompany
            Un objeto del tipo CustomerCompany
        """
        return db.session.query(cls).get(customer_id)

    @classmethod
    def all(cls: SelfCustomerCompany) -> List[SelfCustomerCompany]:
        """Obtener todos los customers

        Returns
        -------
        List[CustomerCompany]
            Una lista de objetos CustomerCompany
        """
        return db.session.query(cls).all()