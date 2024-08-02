from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer, create_engine , DECIMAL, BigInteger,DateTime,Date, Text
from sqlalchemy.orm import DeclarativeBase, declarative_base, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from Core.settings import settings
from datetime import datetime,date

engine = create_engine(url = settings.DB_URL)

session = sessionmaker(bind = engine, autoflush = False, autocommit = False)

def get_db_session():
    db = session()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass

class Admin(Base):
    __tablename__ = "admin"
    admin_id:Mapped[int] = mapped_column(BigInteger, autoincrement = True, index = True, primary_key = True)
    username:Mapped[str] = mapped_column(String(length = 50),nullable=False)
    password:Mapped[str] = mapped_column(String(length=255),nullable=False)
    fullname:Mapped[str] = mapped_column(String(length=100),nullable=False)
    email:Mapped[str] = mapped_column(String(length=100),nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default = datetime.now())
    
class Employee(Base):
    __tablename__ = "employee"
    employee_id:Mapped[int] = mapped_column(BigInteger, autoincrement = True, index = True, primary_key = True)
    username:Mapped[str] = mapped_column(String(length = 50),nullable=False)
    password:Mapped[str] = mapped_column(String(length=255),nullable=False)
    fullname:Mapped[str] = mapped_column(String(length=100),nullable=False)
    email:Mapped[str] = mapped_column(String(length=100),nullable=False)
    role:Mapped[str] = mapped_column(String(length=50),nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default = datetime.now())

class Agent(Base):
    __tablename__ = "agent"
    agent_id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, index=True, primary_key=True)
    username:Mapped[str]= mapped_column(String(length=50), nullable=False)
    password:Mapped[str] = mapped_column(String(length=255), nullable=False)
    fullname:Mapped[str] = mapped_column(String(length=100), nullable=False)
    email:Mapped[str] = mapped_column(String(length=100), nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Define the relationship to Customer (one-to-many)
    customers = relationship("Customer", back_populates="agent")
    commission = relationship("Commission", back_populates = 'agent')

class Customer(Base):
    __tablename__ = "customer"
    customer_id:Mapped[int] = mapped_column(BigInteger, autoincrement=True, index=True, primary_key=True)
    username:Mapped[str] = mapped_column(String(length=50), nullable=False)
    password:Mapped[str] = mapped_column(String(length=255), nullable=False)
    fullname:Mapped[str] = mapped_column(String(length=100), nullable=False)
    email:Mapped[str] = mapped_column(String(length=100), nullable=False)
    phone_number:Mapped[str] = mapped_column(String(length=15), nullable=False)
    date_of_birth:Mapped[date] = mapped_column(Date, nullable=False)
    agent_id:Mapped[int] = mapped_column(BigInteger, ForeignKey('agent.agent_id'), nullable=False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Define the relationship to Agent (many-to-one)
    agent = relationship("Agent", back_populates="customers")

class InsurancePlan(Base):
    __tablename__ = "insuranceplan"
    plan_id:Mapped[int] = mapped_column(BigInteger, primary_key = True, index = True, autoincrement = True)
    plan_name:Mapped[str] = mapped_column(String(length = 100), nullable = False)
    plan_details: Mapped[str] = mapped_column(Text, nullable = True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.now())
    
    schemes = relationship("Scheme", back_populates = 'plan')

class Scheme(Base):
    __tablename__ = "scheme"
    scheme_id: Mapped[int] = mapped_column(BigInteger, primary_key = True, index = True, autoincrement = True)
    scheme_name: Mapped[str] = mapped_column(String(length = 100), nullable = True)
    scheme_details: Mapped[str] = mapped_column(Text, nullable = False)
    plan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('insuranceplan.plan_id'), nullable = False)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.now())
    scheme_tenure:Mapped[int] = mapped_column(Integer, nullable=False)
    scheme_amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable = False)
    
    plan = relationship('InsurancePlan', back_populates = 'schemes')
    policies = relationship('Policy', back_populates = 'scheme')
    employees = relationship('EmployeeScheme', back_populates = 'scheme')

class Policy(Base):
    __tablename__ = "policy"
    policy_id:Mapped[int] = mapped_column(BigInteger, primary_key = True, index = True, autoincrement = True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("customer.customer_id"), nullable = False)
    scheme_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('scheme.scheme_id'), nullable = False)
    policy_details: Mapped[str] = mapped_column(Text, nullable = False)
    premium: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable = False)
    date_issued: Mapped[date] = mapped_column(Date, nullable = False)
    maturity_period: Mapped[int] = mapped_column(Integer, nullable = False)
    policy_lapse_date: Mapped[date] = mapped_column(Date, nullable = False)
    created_at:Mapped[datetime] = mapped_column(DateTime, default = datetime.now())
    
    customer = relationship('Customer')
    scheme = relationship('Scheme', back_populates = 'policies')

class Payment(Base):
    __tablename__ = 'payment'
    payment_id: Mapped[int] = mapped_column(BigInteger, primary_key = True, autoincrement = True, index = True)
    customer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('customer.customer_id'), nullable = False)
    policy_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("policy.policy_id"), nullable = False)
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable = False)
    payment_date: Mapped[date] = mapped_column(Date, nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.now())
    
    customer = relationship('Customer')
    policy = relationship('Policy')

class Commission(Base):
    __tablename__ = 'commission'
    commission_id: Mapped[int] = mapped_column(BigInteger, primary_key = True, index = True, autoincrement = True)
    agent_id :Mapped[int] = mapped_column(BigInteger, ForeignKey('agent.agent_id'), nullable = False)
    policy_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('policy.policy_id'), nullable = False)
    commission_amount: Mapped[float] = mapped_column(DECIMAL(10,2), nullable = False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default = datetime.now())
    
    agent = relationship("Agent", back_populates = 'commission')
    policy = relationship("Policy")

class EmployeeScheme(Base):
    __tablename__ = "employeescheme"
    employeescheme_id: Mapped[int] = mapped_column(BigInteger, primary_key = True, autoincrement = True, index = True)
    employee_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('employee.employee_id'), nullable = False)
    scheme_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('scheme.scheme_id'), nullable = False)

    employee = relationship("Employee")
    scheme = relationship("Scheme", back_populates="employees")