from fastapi import status,HTTPException,Depends
from App.schemas import BaseResponseModel, PolicyResponseSchema, PolicySchema, PolicyReadSchema
from sqlalchemy.orm import Session
from App.models import Customer,Scheme, Policy,Commission
from App.utils import CurrentLoginVerification
from datetime import datetime
from fastapi import APIRouter
from App.database import DataBaseConnection

router = APIRouter()

@router.post("/create_policy", status_code=status.HTTP_201_CREATED, response_model=PolicyResponseSchema)
def create_policy(policy_data: PolicySchema, db: Session = Depends(DataBaseConnection.get_db_session), current_customer: Customer = Depends(CurrentLoginVerification.get_current_customer_user)):
    try:
        scheme = db.query(Scheme).filter(Scheme.scheme_id == policy_data.scheme_id).first()
        if not scheme:
            raise HTTPException(status_code=404, detail="Enter correct Scheme id - Scheme not present")

        premium = ((scheme.scheme_amount)/(scheme.scheme_tenure))*12

        policy_data_dict = policy_data.model_dump()
        policy_data_dict['customer_id'] = current_customer.customer_id
        policy_data_dict['date_issued'] = datetime.now().date()
        policy_data_dict['premium'] = premium

        new_policy = Policy(**policy_data_dict)
        db.add(new_policy)
        db.commit()
        db.refresh(new_policy)

        commission_scheme=Commission(agent_id=current_customer.agent_id,policy_id=new_policy.policy_id,commission_amount=((new_policy.premium)/4))
        db.add(commission_scheme)
        db.commit()
        db.refresh(commission_scheme)

        return {"message": "Policy created successfully", "status": 201, "data": new_policy}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")

@router.get("/read_policy/{policy_id}", response_model=PolicyResponseSchema, status_code=status.HTTP_200_OK)
def read_policy_by_id(policy_id: int, db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")

        return {"message": f"Policy for PolicyID {policy_id} fetched successfully", "status": 200,"data":policy}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")
    
@router.put("/update_policy/{policy_id}", response_model=PolicyResponseSchema, status_code=status.HTTP_200_OK)
def update_policy_by_id(policy_id: int, policy_data: PolicySchema, db: Session = Depends(DataBaseConnection.get_db_session),current_customer: Customer = Depends(CurrentLoginVerification.get_current_customer_user)):
    try:
        policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="Policy  not found")
        
        new_policy = policy_data.model_dump(exclude_unset=True) 

        for key, value in new_policy.items():
            setattr(policy, key, value)
        
        db.commit()
        db.refresh(policy)

        return {"message": f"Policy for PolicyID {policy_id} updated successfully", "status": 200, "data": new_policy}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")

@router.delete("/delete_policy/{policy_id}", status_code=status.HTTP_200_OK, response_model=BaseResponseModel)
def delete_policy_by_id(policy_id: int, db: Session = Depends(DataBaseConnection.get_db_session),current_customer: Customer = Depends(CurrentLoginVerification.get_current_customer_user)):
    try:
        policy = db.query(Policy).filter(Policy.policy_id == policy_id).first()
        if not policy:
            raise HTTPException(status_code=404, detail="policy not found")
        
        db.delete(policy)
        db.commit()

        return {"message": f"policy with PolicyID {policy_id} deleted successfully", "status": 200}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")

@router.get("/read_policy", response_model=PolicyReadSchema, status_code=status.HTTP_200_OK)
def read_all_policy(db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        policys = db.query(Policy).all()
        policys_data=[PolicySchema.from_orm(policy) for policy in policys]
        if not policys:
            raise HTTPException(status_code=404, detail="No Policy found")

        return {"message": "All Policy fetched successfully", "status": 200, "data": policys_data}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")