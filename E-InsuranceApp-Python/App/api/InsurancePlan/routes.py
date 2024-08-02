from fastapi import status,HTTPException,Depends
from App.schemas import BaseResponseModel, InsurancePlanSchema, InsurancePlanResponseSchema, InsuranceReadSchema
from sqlalchemy.orm import Session
from App.models import Employee,InsurancePlan,InsurancePlan
from App.utils import CurrentLoginVerification
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter
from App.database import DataBaseConnection
from Core import loggers

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post("/create_plan/", status_code = status.HTTP_201_CREATED, response_model = InsurancePlanResponseSchema)
def create_plan(plan: InsurancePlanSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    logger.info("Creating Plans...")  
    new_plan = InsurancePlan(**plan.model_dump())
    try:
        db.add(new_plan)
        db.commit()
        db.refresh(new_plan)
    except SQLAlchemyError as e:
        logger.exception("Plan cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the Plan")
    logger.info("Plan registered successfully")
    return {"message": "Insurance createdsuccessfully", "status": status.HTTP_201_CREATED,"data": new_plan}

@router.get("/read_insurance_plan/", response_model=InsuranceReadSchema)
def read_insurance_plan(db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        insurances = db.query(InsurancePlan).all()
        if not insurances:
            logger.warning("Insurance Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insurance Not Found")
        logger.info("Insurances Retrieved Successfully from Database")
        plans = [
            ins for ins in insurances
        ]
        return {"message": "Insurance plans read successfully", "status": status.HTTP_200_OK, "data": plans}
    
    except HTTPException as e:
        logger.error(f"Error retrieving insurances from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving insuarnces from database")

@router.get("/read_insuranceplan_by_id/", response_model=InsurancePlanResponseSchema)
def read_plans_by_id(plan_id:int,db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        plans = db.query(InsurancePlan).filter(InsurancePlan.plan_id == plan_id).first()
        if not plans:
            logger.warning("Plans Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plans Not Found")
        logger.info("Plans Retrieved Successfully from Database")
        return {"message": "Insurance plans read successfully", "status": status.HTTP_200_OK, "data": plans}
    
    except HTTPException as e:
        logger.error(f"Error retrieving customers from database: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error retrieving customers from database")

@router.put("/update_insurance_plan/{plan_id}", response_model=InsurancePlanResponseSchema)
def update_plan(plan_id: int, plan_update:InsurancePlanSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        plan = db.query(InsurancePlan).filter(InsurancePlan.plan_id == plan_id).first()
        if not plan:
            logger.warning("Plan Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan Not Found")
        
        for key, value in plan_update.model_dump(exclude_unset=True).items():
            setattr(plan, key, value)
        
        db.commit()
        db.refresh(plan)
        
        logger.info("Plan Updated Successfully")
        return {"message": "Insurance plans updated successfully", "status": status.HTTP_200_OK, "data": plan}
    
    except HTTPException as e:
        logger.error(f"Error updating plan: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating plan")

@router.delete("/delet_plan/{plan_id}", response_model=BaseResponseModel)
def delete_plan(plan_id: int, db: Session = Depends(DataBaseConnection.get_db_session), current_user: Employee = Depends(CurrentLoginVerification.get_current_employee_user)):
    try:
        plan = db.query(InsurancePlan).filter(InsurancePlan.plan_id==plan_id).first()
        if not plan:
            logger.warning("Plan Not Found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan Not Found")
        
        db.delete(plan)
        db.commit()
        
        logger.info("Customer Deleted Successfully")
        return {"message":"Deleted","status":200}
    
    except HTTPException as e:
        logger.error(f"Error deleting plan: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting Plan")