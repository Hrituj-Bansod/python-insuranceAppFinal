from fastapi import FastAPI
from App.api.Admin.routes import router as admin_router
from App.api.Login.routes import router as login_router
from App.api.Customer.routes import router as customer_router
from App.api.Employee.routes import router as employee_router
from App.api.Agent.routes import router as agent_router
from App.api.InsurancePlan.routes import router as insuranceplan_router
from App.api.Scheme.routes import router as scheme_router
from App.api.Policy.routes import router as policy_router
from App.api.Commission.routes import router as commission_router

app=FastAPI()

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(login_router,prefix="/login",tags=["Login"])
app.include_router(customer_router,prefix="/customer",tags=["Customer"])
app.include_router(employee_router,prefix="/employee",tags=["Employee"])
app.include_router(agent_router,prefix="/agent",tags=["Agent"])
app.include_router(insuranceplan_router,prefix="/insuranceplan",tags=["InsurancePlan"])
app.include_router(scheme_router,prefix="/scheme",tags=["Scheme"])
app.include_router(policy_router,prefix="/policy",tags=["Policy"])
app.include_router(commission_router,prefix="/commission",tags=["Commission"])