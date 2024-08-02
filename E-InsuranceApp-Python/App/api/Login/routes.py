from fastapi import status,HTTPException,Depends
from App.schemas import LoginSchema
from sqlalchemy.orm import Session
from App.models import Admin, Employee, Customer, Agent
from App.utils import PasswordUtils,JWTUtils, UserRole
from fastapi import APIRouter
from App.database import DataBaseConnection
from Core import loggers

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post('/login/',status_code=200)
def login(user: LoginSchema, db: Session = Depends(DataBaseConnection.get_db_session)):
    logger.info("Login Attempted!!!")
    try : 
        user_in_db = None
        if user.role == UserRole.admin:
            user_in_db = db.query(Admin).filter(Admin.email == user.email).first()
        elif user.role == UserRole.employee:
            user_in_db = db.query(Employee).filter(Employee.email == user.email).first()
        elif user.role == UserRole.customer:
            user_in_db = db.query(Customer).filter(Customer.email == user.email).first()
        elif user.role == UserRole.agent:
            user_in_db = db.query(Agent).filter(Agent.email == user.email).first()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")

        if not user_in_db or not PasswordUtils.verify_password(user.password, user_in_db.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    except HTTPException as e:
        logger.exception(f"Error in Logging {e}")
        raise HTTPException(status_code=500, detail="An error occurred while Logging")
    user_data = {"username": user_in_db.username, "role": user.role}
    access_token = JWTUtils.encode_jwt(payload=user_data)
    return {"access_token": access_token}
