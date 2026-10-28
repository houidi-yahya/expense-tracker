from decimal import Decimal
import httpx
from fastapi import APIRouter, HTTPException , Depends
from pydantic import HttpUrl
import httpx
from database import get_db
from models import ExpenseCreate, ExpenseBack , ExpensePatch
from psycopg import Connection, connection
from routes.auth import get_current_user

router = APIRouter(prefix="/expenses")

@router.get("",response_model=list[ExpenseBack])
def get_expenses(user_id: int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    rows=conn.execute(
        "select *from expenses where user_id=%s;",
        (user_id,)
    ).fetchall()
    return rows

@router.post("/",response_model=ExpenseBack,status_code=201)
def expense_create(expense:ExpenseCreate,user_id: int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    row=conn.execute(
        "insert into expenses (object,price,category,user_id) values(%s,%s,%s,%s) returning *;",
        (expense.object,expense.price,expense.category,user_id)
    ).fetchone()
    conn.commit()
    return row


@router.get("/total")
async def total(currency : str, user_id : int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    currency=currency.upper()
    row=conn.execute(
        "Select coalesce(sum(price),0) as total from expenses where user_id=%s;",
        (user_id,)
    ).fetchone()
    url= f"https://api.frankfurter.dev/v2/rate/USD/{currency}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
        response.raise_for_status()
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Currency API timed out")
    except httpx.ConnectError:
        raise HTTPException(status_code=502, detail="Cannot connect to currency API")
    except httpx.HTTPStatusError as e:
        if e.response.status_code==404:
            raise HTTPException(status_code=404 , detail="invalid currency") from e
        raise HTTPException(status_code=404 , detail="invalid currency") from e
    data=response.json()
    rate=data["rate"]
    tot=row["total"]*Decimal(str(rate))
    return  {"total" : f"{tot:.2f}", "currency" : currency} 

@router.get("/summary")
async def summary(currency : str, user_id : int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    currency=currency.upper()
    row=conn.execute(
        "Select category,coalesce(sum(price),0) as total from expenses where user_id=%s group by category;",
        (user_id,)
    ).fetchall()
    row1=conn.execute(
        "Select extract(month from created_at) as month ,extract(year from created_at) as year ,coalesce(sum(price),0) as total from expenses where user_id=%s group by extract(month from created_at),extract(year from created_at) ;",
        (user_id,)
    ).fetchall()
    url= f"https://api.frankfurter.dev/v2/rate/USD/{currency}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
        response.raise_for_status()
    except httpx.Timeout:
        raise HTTPException(status_code=504, detail="Currency API timed out")
    except httpx.ConnectionError:
        raise HTTPException(status_code=502, detail="Cannot connect to currency API")
    except httpx.HTTPError as e:
        if e.response.status_code==404:
            raise HTTPException(status_code=404 , detail="invalid currency") from e
        raise HTTPException(status_code=404 , detail="invalid currency") from e
    data=response.json()
    rate = Decimal(str(data["rate"]))
    for r in row:
        r["total"] = (r["total"] * rate).quantize(Decimal("0.01"))

    for r in row1:
        r["total"] = (r["total"] * rate).quantize(Decimal("0.01"))
    return {"by_month" : row1,"by_category" : row}
    

   

@router.get("/{expense_id}",response_model=ExpenseBack)
def get_expense_id(expense_id:int,user_id: int = Depends(get_current_user),conn : Connection = Depends(get_db)) : 
    row=conn.execute(
        "select * from expenses where (id=(%s) and user_id=%s); ",
        (expense_id,user_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404 ,detail="expense not found")
    else :
        return row

@router.delete("/{expense_id}",status_code=204)
def delete_note(expense_id:int,user_id: int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    row=conn.execute(
        "delete from expenses where (id=(%s) and user_id=%s) returning id;",
        (expense_id,user_id,)
    ).fetchone()
    conn.commit()
    if row is None : 
        raise HTTPException(status_code=404 , detail="expense not found")
    return {"message" : "deleted"}

@router.patch("/{expense_id}",response_model=ExpenseBack)
def patch_note(expense:ExpensePatch,expense_id:int,user_id: int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    row=conn.execute(
        "update expenses e set object=coalesce(%s,e.object), price=coalesce(%s,e.price),category=coalesce(%s,e.category) where (id=(%s) and user_id=%s) RETURNING*;",
        (expense.object,expense.price,expense.category,expense_id,user_id,)
    ).fetchone()
    conn.commit()
    if row is None:
        raise HTTPException(status_code=404,detail="expense not found")
    return row


@router.put("/{expense_id}",response_model=ExpenseBack)
def edit_note(expense:ExpenseCreate,expense_id:int,user_id: int = Depends(get_current_user),conn : Connection = Depends(get_db)):
    row=conn.execute(
        "update expenses set object=%s ,price=%s,category=%s where (id=(%s) and user_id=%s) RETURNING*;",
        (expense.object,expense.price,expense.category,expense_id,user_id)
    ).fetchone()
    conn.commit()
    if row is None:
        raise HTTPException(status_code=404,detail="expense not found")
    return row



