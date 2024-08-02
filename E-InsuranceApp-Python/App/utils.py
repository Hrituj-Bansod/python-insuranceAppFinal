from passlib.context import CryptContext
from datetime import datetime, timedelta
from jwt import PyJWTError
import jwt
from Core.settings import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from fastapi import status, Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from .database import DataBaseConnection
from enum import Enum

class PasswordUtils:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(raw_password: str, hashed_password: str) -> bool:
        return PasswordUtils.pwd_context.verify(raw_password, hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        return PasswordUtils.pwd_context.hash(password)
    
class EmailUtils:
    @staticmethod
    def send_email(to_email: str, from_email: str = settings.EMAIL, password: str = settings.PASSWORD, registration_data=None, Subject=None, body=None) -> None:
        """Send an email using SMTP."""
        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL
        msg['To'] = to_email
        msg['Subject'] = Subject
        if body is None:
            body = f"your login details are\n{registration_data}"
        msg.attach(MIMEText(body, 'plain'))
        try:
            server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
            server.starttls()
            
            server.login(from_email, password)
            
            server.sendmail(from_email, to_email, msg.as_string())
            
            server.quit()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

class JWTUtils:
    SECRET_KEY = settings.SECRET_KEY 
    ALGORITHM = settings.ALGORITHM

    @staticmethod
    def encode_jwt(payload: dict) -> str:
        if "exp" not in payload:
            payload["exp"] = datetime.utcnow() + timedelta(hours=1)
        encoded_jwt = jwt.encode(payload, JWTUtils.SECRET_KEY, algorithm=JWTUtils.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_jwt(token: str) -> dict:
        try:
            decoded_payload = jwt.decode(token, JWTUtils.SECRET_KEY, algorithms=[JWTUtils.ALGORITHM])
        except PyJWTError:
            raise HTTPException(detail="Invalid JWT Token", status_code=401)
        return decoded_payload
    
class CurrentLoginVerification:
    @staticmethod
    def get_current_admin_user(api_key: str = Security(APIKeyHeader(name="Authorization")), db: Session = Depends(DataBaseConnection.get_db_session)):
        from App.models import Admin  # Defer import to avoid circular import
        try:
            payload = JWTUtils.decode_jwt(api_key)
            username = payload.get("username")
            role = payload.get("role")

            if role != UserRole.admin:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

            admin_user = db.query(Admin).filter(Admin.username == username).first()
            if not admin_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user does not exist")
            
            return admin_user
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        
    @staticmethod
    def get_current_customer_user(api_key: str = Security(APIKeyHeader(name="Authorization")), db: Session = Depends(DataBaseConnection.get_db_session)):
        from App.models import Customer  # Defer import to avoid circular import
        try:
            payload = JWTUtils.decode_jwt(api_key)
            username = payload.get("username")
            role = payload.get("role")

            if role != UserRole.customer:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

            customer_user = db.query(Customer).filter(Customer.username == username).first()
            if not customer_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user does not exist")
            
            return customer_user
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        
    @staticmethod
    def get_current_employee_user(api_key: str = Security(APIKeyHeader(name="Authorization")), db: Session = Depends(DataBaseConnection.get_db_session)):
        from App.models import Employee  # Defer import to avoid circular import
        try:
            payload = JWTUtils.decode_jwt(api_key)
            username = payload.get("username")
            role = payload.get("role")

            if role != UserRole.employee:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

            employee_user = db.query(Employee).filter(Employee.username == username).first()
            if not employee_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user does not exist")
            
            return employee_user
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

class UserRole(str, Enum):
    admin = "Admin"
    employee = "Employee"
    customer = "Customer"
    agent = "Agent"     