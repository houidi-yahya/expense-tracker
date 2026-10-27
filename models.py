from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel,EmailStr

class ExpenseCreate(BaseModel):
    object:str = "not_specified"
    price:Decimal
    category:str = "other"


class ExpenseBack(BaseModel):
    id : int
    object:str
    price:Decimal
    user_id:int
    created_at:datetime
    category:str


class ExpensePatch(BaseModel):
    object:str | None=None
    price:Decimal | None=None
    category:str | None=None

class create_user(BaseModel):
    id:int
    email:EmailStr
    created_at:datetime


class connect_user(BaseModel):
    email:EmailStr
    password:str


