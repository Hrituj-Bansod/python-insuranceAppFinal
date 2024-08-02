from fastapi import status, HTTPException, Depends
from App.schemas import AdminRegistrationSchema, AdminResponseSchema
from App.models import Admin 
from sqlalchemy.orm import Session
from App.utils import EmailUtils, PasswordUtils
from sqlalchemy.exc import SQLAlchemyError
from App.database import DataBaseConnection
from fastapi import APIRouter
from Core import loggers

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post("/admin-register", status_code = status.HTTP_201_CREATED, response_model = AdminResponseSchema, response_model_exclude = {"data": ["password"]})
def register_admin(admin: AdminRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session)):
    logger.info("Registering the Admin...")
    admin_exists = db.query(Admin).filter(Admin.username == admin.username).first()
    if admin_exists:
        logger.exception("Admin already Exists")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = PasswordUtils.hash_password(admin.password)
    new_admin = Admin(
        username = admin.username,
        password = hashed_password,
        fullname = admin.fullname,
        email = admin.email
    )
    
    try:
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        EmailUtils.send_email(new_admin.email,Subject="Credential Details for E-Insuarance App",
                              body=f"""Welcome to the Application... \n Dear {new_admin.fullname}, 
                              \n We are pleased to inform you that your e-Insurance account has been successfully created. 
                              Below you will find your login credentials and instructions for accessing your account. 
                              \n User Name: {new_admin.username} \n Password: {admin.password}""")
    except SQLAlchemyError as e:
        logger.exception("Admin cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the Admin")
    logger.info("Admin registered successfully")
    return {"message": "Admin registered successfully", "status": 201, "data": new_admin}