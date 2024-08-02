from fastapi import FastAPI,status,HTTPException,Depends,Security
from fastapi.security import APIKeyHeader
from App.schemas import AgentRegistrationSchema, AgentResponseModel, AgentReadSchema, BaseResponseModel
from App.models import Agent, Admin
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from App.utils import EmailUtils,PasswordUtils, CurrentLoginVerification
from App.database import DataBaseConnection
from Core import loggers

from fastapi import APIRouter

router = APIRouter()

log_file = "insurance.log"
logger = loggers.setup_logger(log_file)

@router.post("/agent-register", status_code = status.HTTP_201_CREATED, response_model = AgentResponseModel, response_model_exclude = {"data": ["password"]})
def register_agent(agent: AgentRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    logger.info("Registering the Agent...")
    agent_exists = db.query(Agent).filter(Agent.username == agent.username).first()
    if agent_exists:
        logger.exception("Agent already Exists")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = PasswordUtils.hash_password(agent.password)
    new_agent = Agent(
        username = agent.username,
        password = hashed_password,
        fullname = agent.fullname,
        email = agent.email
    )
    
    try:
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        EmailUtils.send_email(new_agent.email,Subject="Credential Details for E-Insuarance App",
                              body=f"""Welcome to the Application... \n Dear {new_agent.fullname}, 
                              \n We are pleased to inform you that your e-Insurance account has been successfully created. 
                              Below you will find your login credentials and instructions for accessing your account. 
                              \n User Name: {new_agent.username} \n Password: {agent.password}""")
    except SQLAlchemyError as e:
        logger.exception("Agent cannot be created")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while creating the Agent")
    logger.info("Agent registered successfully")
    return {"message": "Agent registered successfully", "status": 201, "data": new_agent}

@router.get("/agent/read_all/", response_model = AgentReadSchema, response_model_exclude={'password'})
def read_agent(db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    agents = db.query(Agent).all()
    if not agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {'data': agents}

@router.get("/agent/read_by_id/{agent_id}", response_model = AgentResponseModel)
def read_agent_by_id(agent_id: int, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent read successfully", "status": status.HTTP_200_OK, "data": agent}

@router.put("/agent/update/{agent_id}", response_model=AgentResponseModel)
def update_agent(agent_id: int, agent: AgentRegistrationSchema, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    hashed_password = PasswordUtils.hash_password(agent.password)
    db_agent.username = agent.username
    db_agent.password = hashed_password
    db_agent.fullname = agent.fullname
    db_agent.email = agent.email
    
    try:
        db.commit()
        db.refresh(db_agent)
    except SQLAlchemyError as e:
        logger.exception("agent cannot be updated")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while updating the agent")
    return {"message": "agent updated successfully", "status": 200, "data": db_agent}

@router.delete("/agent/delete/{agent_id}", response_model=BaseResponseModel)
def delete_agent(agent_id: int, db: Session = Depends(DataBaseConnection.get_db_session), current_admin: Admin = Depends(CurrentLoginVerification.get_current_admin_user)):
    db_agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
    if not db_agent:
        raise HTTPException(status_code=404, detail="agent not found")
    
    try:
        db.delete(db_agent)
        db.commit()
    except SQLAlchemyError as e:
        logger.exception("agent cannot be deleted")
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while deleting the agent")
    return {"message": "agent deleted successfully", "status": 200}
