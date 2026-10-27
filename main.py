from fastapi import FastAPI
from routes import expenses,auth
app=FastAPI()

app.include_router(expenses.router)
app.include_router(auth.router)
