from fastapi import FastAPI,status,HTTPException,Depends
from fastapi.security import APIKeyHeader
from App.schemas import CustomerRegistrationSchema, CustomerReadSchema, CustomerResponseSchema, CustomersListResponseSchema, BaseResponseModel
from sqlalchemy.orm import Session
from App.models import Customer
from App.utils import EmailUtils,PasswordUtils
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter
from App.database import DataBaseConnection
from Core import loggers

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post("/customer-register", status_code = status.HTTP_201_CREATED, response_model = CustomerResponseSchema, response_model_exclude = {"data": ["password"]})
def register_customer(customer: CustomerRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session)):
    logger.info("Registering the Customer...")
    customer_exists = db.query(Customer).filter(Customer.username == customer.username).first()
    if customer_exists:
        logger.exception("Customer already Exists")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = PasswordUtils.hash_password(customer.password)
    new_customer = Customer(
        username = customer.username,
        password = hashed_password,
        fullname = customer.fullname,
        email = customer.email,
        phone_number = customer.phone_number,
        date_of_birth = customer.date_of_birth,
        agent_id = customer.agent_id
    )
    
    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        EmailUtils.send_email(new_customer.email,Subject="Credential Details for E-Insuarance App",
                              body=f"""Welcome to the Application... \n Dear {new_customer.fullname}, \n 
                              We are pleased to inform you that your e-Insurance account has been successfully created. 
                              Below you will find your login credentials and instructions for accessing your account. 
                              \n User Name: {new_customer.username} \n Password: {customer.password}""")
    except SQLAlchemyError as e:
        logger.exception("Customer cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Agent Not Exist {e}")
    logger.info("Customer registered successfully")
    return {"message": "Customer registered successfully", "status": 201, "data": new_customer}
    
@router.get("/read_customer/", response_model=CustomersListResponseSchema)
def read_customers(db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        customers = db.query(Customer).all()
        if not customers:
            logger.warning("Customer Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customers Not Found")
        logger.info("Customers Retrieved Successfully from Database")
        customers_list = [
            customer for customer in customers
        ]
        return {"message": "Customer read successfully", "status": 200, "data": customers_list}
    
    except HTTPException as e:
        logger.error(f"Error retrieving customers from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving customers from database")

@router.get("/read_customer_id/", response_model=CustomerResponseSchema,response_model_exclude={"data":["password"]})
def read_customers_by_id(customer_id:int,db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        customers = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customers:
            logger.warning("Customer Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found")
        logger.info("Customers Retrieved Successfully from Database")
        return {"message": "Customers Retrieved Successfully from Database", "status": 200, "data": customers}
    
    except HTTPException as e:
        logger.error(f"Error retrieving customers from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving customers from database")

@router.put("/update_customer/{customer_id}", response_model=CustomerResponseSchema, response_model_exclude={"data": ["password"]})
def update_customer(customer_id: int, customer_update: CustomerRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            logger.warning("Customer Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found")
        
        for key, value in customer_update.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        
        db.commit()
        db.refresh(customer)
        
        logger.info("Customer Updated Successfully")
        return {"message": "Customer Updated Successfully", "status": 200, "data": customer}
    
    except HTTPException as e:
        logger.error(f"Error updating customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating customer")

@router.delete("/delete_customer/{customer_id}", response_model=CustomerResponseSchema, response_model_exclude={"data": ["password"]})
def delete_customer(customer_id: int, db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        customer = db.query(Customer).filter(Customer.customer_id == customer_id).first()
        if not customer:
            logger.warning("Customer Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Not Found")
        
        db.delete(customer)
        db.commit()
        
        logger.info("Customer Deleted Successfully")
        return {"message": "Customer Deleted Successfully", "status": 200, "data": customer}
    
    except HTTPException as e:
        logger.error(f"Error deleting customer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting customer")
