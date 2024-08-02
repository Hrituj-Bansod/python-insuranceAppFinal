from fastapi import status,HTTPException,Depends
from App.schemas import BaseResponseModel, EmployeeRegistrationSchema, EmployeeReadSchema, EmployeeListSchema, EmployeeResponseSchema
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from App.models import Employee, Admin
from App.utils import EmailUtils,PasswordUtils,CurrentLoginVerification
from App.database import DataBaseConnection
from fastapi import APIRouter
from Core import loggers

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post("/employee-register", status_code = status.HTTP_201_CREATED, response_model = EmployeeResponseSchema, response_model_exclude = {"data": ["password"]})
def register_employee(employee: EmployeeRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    logger.info("Registering the Employee...")
    employee_exists = db.query(Employee).filter(Employee.username == employee.username).first()
    if employee_exists:
        logger.exception("Employee already Exists")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = PasswordUtils.hash_password(employee.password)
    new_employee = Employee(
        username = employee.username,
        password = hashed_password,
        fullname = employee.fullname,
        email = employee.email,
        role = employee.role
    )
    
    try:
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        EmailUtils.send_email(new_employee.email,Subject="Credential Details for E-Insuarance App",
                              body=f"""Welcome to the Application... \n Dear {new_employee.fullname}, \n 
                              We are pleased to inform you that your e-Insurance account has been successfully created. 
                              Below you will find your login credentials and instructions for accessing your account. 
                              \n User Name: {new_employee.username} \n Password: {employee.password}""")
    except SQLAlchemyError as e:
        logger.exception("Employee cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the Employee")
    logger.info("Employee registered successfully")
    return {"message": "Employee registered successfully", "status": 201, "data": new_employee}

@router.get("/employee/read_all/", response_model = EmployeeReadSchema)
def read_employees(db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    employees = db.query(Employee).all()
    return {"message": "Employee read successfully", "status": 201,'data': employees}

@router.get("/employees/read_by_id/{employee_id}", response_model = EmployeeResponseSchema)
def read_employee_by_id(employee_id: int, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee read successfully", "status": status.HTTP_200_OK, "data": employee}

@router.put("/employees/update/{employee_id}", response_model=EmployeeResponseSchema)
def update_employee(employee_id: int, employee: EmployeeRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    hashed_password = PasswordUtils.hash_password(employee.password)
    db_employee.username = employee.username
    db_employee.password = hashed_password
    db_employee.fullname = employee.fullname
    db_employee.email = employee.email
    db_employee.role = employee.role
    
    try:
        db.commit()
        db.refresh(db_employee)
    except SQLAlchemyError as e:
        logger.exception("Employee cannot be updated")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the Employee")
    return {"message": "Employee updated successfully", "status": 200, "data": db_employee}

@router.delete("/employees/delete/{employee_id}", response_model=BaseResponseModel)
def delete_employee(employee_id: int, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    try:
        db.delete(db_employee)
        db.commit()
    except SQLAlchemyError as e:
        logger.exception("Employee cannot be deleted")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the Employee")
    return {"message": "Employee deleted successfully", "status": 200}
