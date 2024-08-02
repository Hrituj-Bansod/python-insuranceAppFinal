from fastapi import status,HTTPException,Depends
from App.schemas import SchemeSchema, SchemeResponseSchema, SchemeReadSchema, EmployeeSchemeSchema, BaseResponseModel
from sqlalchemy.orm import Session
from App.models import Employee, Scheme, EmployeeScheme
from App.utils import CurrentLoginVerification
from App.database import DataBaseConnection
from Core import loggers
from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post("/create_scheme/", status_code = status.HTTP_201_CREATED, response_model = SchemeResponseSchema)
def create_scheme(scheme: SchemeSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    logger.info("Creating Schemes...")  
    new_scheme = Scheme(**scheme.model_dump())
    try:
        db.add(new_scheme)
        db.commit()
        db.refresh(new_scheme)

        employee_scheme = EmployeeScheme(employee_id=current_user.employee_id, scheme_id=new_scheme.scheme_id)
        db.add(employee_scheme)
        db.commit()

    except SQLAlchemyError as e:
        logger.exception("Scheme cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the Scheme")
    logger.info("Scheme registered successfully")
    return {"message": "Scheme created successfully", "status": status.HTTP_201_CREATED,"data": new_scheme}

@router.get("/read_schemes/", response_model=SchemeReadSchema)
def read_schemes(db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        schemes = db.query(Scheme).all()
        if not schemes:
            logger.warning("Scheme Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme Not Found")
        logger.info("Scheme Retrieved Successfully from Database")
        read_schemes = [
            scheme for scheme in schemes
        ]
        return {"message": "Schemes read successfully", "status": status.HTTP_200_OK, "data": read_schemes}
    
    except HTTPException as e:
        logger.error(f"Error retrieving schemes from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving schemes from database")

@router.get("/read_schemes_by_id/{scheme_id}/", response_model=SchemeResponseSchema)
def read_schemes_by_id(schemes_id:int,db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        schemes = db.query(Scheme).filter(Scheme.scheme_id == schemes_id).first()
        if not schemes:
            logger.warning("Scheme Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="scheme Not Found")
        logger.info("Schemes Retrieved Successfully from Database")
        return {"message": "Schemes read successfully", "status": status.HTTP_200_OK, "data": schemes}
    
    except HTTPException as e:
        logger.error(f"Error retrieving Scheme from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving Scheme from database")

@router.put("/update_scheme/{scheme_id}", response_model=SchemeResponseSchema)
def update_scheme(scheme_id: int, db_scheme: SchemeSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    scheme = db.query(Scheme).filter(Scheme.scheme_id == scheme_id).first()
    if not scheme:
        logger.warning("Plan Not Found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan Not Found")
    
    scheme.scheme_name = Scheme.scheme_name
    scheme.scheme_details = Scheme.scheme_details
    scheme.price = Scheme.price
    scheme.scheme_tenure = Scheme.scheme_tenure
    scheme.scheme_amount = Scheme.scheme_amount
    
    try:
        db.commit()
        db.refresh(scheme)
    except SQLAlchemyError as e:
        logger.exception("scheme cannot be updated")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the scheme")
    return {"message": "scheme updated successfully", "status": 200, "data": scheme}

@router.delete("/delet_scheme/{scheme_id}", response_model=BaseResponseModel)
def delete_scheme(scheme_id: int, db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        scheme = db.query(Scheme).filter(Scheme.scheme_id == scheme_id).first()
        if not scheme:
            logger.warning("Scheme Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheme Not Found")
        
        db.delete(scheme)
        db.commit()
        
        logger.info("Scheme Deleted Successfully")
        return {"message":"Deleted","status":200}
    
    except HTTPException as e:
        logger.error(f"Error deleting scheme: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting scheme")