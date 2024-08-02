from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional,List
import re
from Core import loggers
from datetime import date, datetime
from .utils import UserRole

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

class BaseResponseModel(BaseModel):
    message: str
    status: int

class AdminRegistrationSchema(BaseModel):    
    username: str = Field(default=" ",pattern=r"^[a-zA-Z0-9.]{3,15}$")
    password: str = Field(default=" ",min_length=8,max_length=250,description="Minimun 8 long,1 Caps, 1 Special Character and 1 Num")
    fullname: str = Field(default=" ",min_length=1,max_length=50)
    email: EmailStr = Field(default=" ",emmin_length=1,max_length=100)
    created_at: Optional[datetime] = None
    
    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError('Password must contain at least one special character')
        if not re.search(r"\d", value):
            raise ValueError('Password must contain at least one number')
        return value

class EmployeeRegistrationSchema(BaseModel):    
    username: str = Field(...,pattern=r"^[a-zA-Z0-9.]{3,15}$")
    password: str = Field(...,min_length=8,max_length=250,description="Minimun 8 long,1 Caps, 1 Special Character and 1 Num")
    fullname: str = Field(...,min_length=1,max_length=50)
    email: EmailStr = Field(...,min_length=1,max_length=100)
    role: str = Field(...,min_length=1,max_length=100)
    created_at: Optional[datetime] = None
    
    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError('Password must contain at least one special character')
        if not re.search(r"\d", value):
            raise ValueError('Password must contain at least one number')
        return value

class AdminResponseSchema(BaseResponseModel):
    data:AdminRegistrationSchema

class EmployeeResponseSchema(BaseResponseModel):
    data:EmployeeRegistrationSchema

class EmployeeListSchema(BaseModel):
    username: str = Field(...,pattern=r"^[a-zA-Z0-9.]{3,15}$")
    fullname: str = Field(...,min_length=1,max_length=50)
    email: EmailStr = Field(...,min_length=1,max_length=100)
    role: str = Field(...,min_length=1,max_length=100)
    created_at: Optional[datetime] = None

class EmployeeReadSchema(BaseModel):
    data: List[EmployeeListSchema]

class CustomerRegistrationSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")
    fullname: str = Field(min_length=1, max_length=20, description="Last name must be between 1 and 20 characters long.")
    email: EmailStr = Field(description = "THe Email entered should be valid")
    phone_number: str = Field(pattern=r'^\+?\d{1,15}$')
    date_of_birth: date = Field(date)
    agent_id: int
    created_at: Optional[datetime] = Field(datetime.now())
    
    @field_validator('password')
    def validate_password(cls, v):
        if (len(v) < 8 or
            not re.search("[a-z]", v) or
            not re.search("[A-Z]", v) or
            not re.search("[0-9]", v) or
            not re.search("[@$!%*?&]", v)):
            logger.exception("Password incorrect")
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return v
    
    class Config:
        from_attributes=True
        
class AgentRegistrationSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    password: str = Field(min_length=8, max_length=250, description="Password must be between 8 and 250 characters long.")
    fullname: str = Field(min_length=1, max_length=20, description="Last name must be between 1 and 20 characters long.")
    email: EmailStr = Field(description = "THe Email entered should be valid")
    created_at: Optional[datetime] = Field(datetime.now())

    @field_validator('password')
    def validate_password(cls, v):
        if (len(v) < 8 or
            not re.search("[a-z]", v) or
            not re.search("[A-Z]", v) or
            not re.search("[0-9]", v) or
            not re.search("[@$!%*?&]", v)):
            logger.exception("Password incorrect")
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
        return v

class CustomerResponseSchema(BaseResponseModel):
    data: CustomerRegistrationSchema

class AgentResponseModel(BaseResponseModel):
    data: AgentRegistrationSchema

class AgentListSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    fullname: str = Field(min_length=1, max_length=20, description="Last name must be between 1 and 20 characters long.")
    email: EmailStr = Field(description = "THe Email entered should be valid")
    created_at: Optional[datetime] = Field(datetime.now())

class AgentReadSchema(BaseModel):
    data: List[AgentListSchema]

class LoginSchema(BaseModel):
    email: EmailStr = Field(default=" ")
    password: str = Field(default=" ")
    role : UserRole

class CustomerReadSchema(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$", description="Username must be between 3 and 50 characters long and can contain letters, numbers, hyphens, and underscores.")
    fullname: str = Field(min_length=1, max_length=20, description="Last name must be between 1 and 20 characters long.")
    email: EmailStr = Field(description = "THe Email entered should be valid")
    phone_number: str = Field(pattern=r'^\+?\d{1,15}$')
    date_of_birth: date = Field(date)
    agent_id: int
    created_at: Optional[datetime] = Field(datetime.now())
    
class CustomersListResponseSchema(BaseModel):
    data: List[CustomerReadSchema]

class InsurancePlanSchema(BaseModel):
    plan_name: str = Field(min_length = 3, max_length = 100, description = 'The plam must be defined within the given length of 3 to 100')
    plan_details: str 
    created_at: Optional[datetime] = Field(datetime.now())

class InsurancePlanResponseSchema(BaseResponseModel):
    data: InsurancePlanSchema

class InsuranceReadSchema(BaseModel):
    data: List[InsurancePlanSchema]

class SchemeSchema(BaseModel):
    scheme_name: str = Field(min_length = 3, max_length = 100, description = 'Enter the correct scheme name')
    scheme_details: str = Field(min_length = 3, description = "You must enter the text having length more than 3")
    plan_id: int
    price: float
    scheme_tenure: int
    scheme_amount: float
    created_at: Optional[datetime] = Field(datetime.now())

class SchemeResponseSchema(BaseResponseModel):
    data: SchemeSchema

class SchemeReadSchema(BaseModel):
    data: List[SchemeSchema]

class PolicySchema(BaseModel):
    scheme_id: int
    policy_details: str = Field(min_length = 3, description = 'Enter the valid description for the given policy')
    maturity_period: int
    policy_lapse_date: date

    class Config:
        from_attributes = True

class PolicyResponseSchema(BaseResponseModel):
    data: PolicySchema

class PolicyReadSchema(BaseModel):
    data: List[PolicySchema]

class AgentData(BaseModel):
    agent_id: int

class CommissionSchema(BaseModel):
    agent_id: int
    policy_id: int
    commission_amount: float = Field(gt = 0)
    created_at: Optional[datetime] = Field(datetime.now())

    class Config:
        from_attributes = True

class CommissionResponseSchema(BaseResponseModel):
    data: List[AgentData]
    total_commission: float

class EmployeeSchemeSchema(BaseModel):
    employee_id: int
    scheme_id: int

class PaymentSchema(BaseModel):
    customer_id: int
    policy_id: int
    amount: float = Field(gt = 0)
    payment_date: date
    created_at: Optional[datetime] = Field(datetime.now())