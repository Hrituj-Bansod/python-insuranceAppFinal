from fastapi import status,HTTPException,Depends
from App.schemas import CommissionSchema, CommissionResponseSchema
from sqlalchemy.orm import Session
from App.models import Commission
from App.utils import CurrentLoginVerification
from sqlalchemy.exc import SQLAlchemyError
from fastapi import APIRouter
from App.database import DataBaseConnection

router = APIRouter()

@router.get("/get_agent_commission/{agent_id}", response_model=CommissionResponseSchema, status_code=status.HTTP_200_OK)
def get_agent_commission(agent_id: int, db: Session = Depends(DataBaseConnection.get_db_session)):
    try:
        agent = db.query(Commission).filter(Commission.agent_id == agent_id).all()     
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent_data = [CommissionSchema.from_orm(plan) for plan in agent]
        total_commission = sum(agent.commission_amount for agent in agent)   

        return {"message": f"Agent Data for AgentID:{agent_id} fetched successfully", "status": 200,"data":agent_data, "total_commission": total_commission}    

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error - {e}")