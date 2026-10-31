from fastapi import APIRouter, HTTPException , Depends, Header
from database import get_db
from models import ExpenseCreate, ExpenseBack , ExpensePatch , connect_user , create_user
from psycopg import Connection , errors
import bcrypt 
from dotenv import load_dotenv
from datetime import datetime,timedelta,timezone
import jwt
from database import get_env
SECRET_KEY=get_env("JWT_SECRET")
ALGORITHM="HS256"

def get_current_user(authorization: str | None = Header(default=None)) -> int:
    if authorization is None  : 
        raise HTTPException(status_code=401 , detail = "invalid header")
    elif not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401 , detail="missing token")
    else: 
        token=authorization.split(" ",1)[1]
        try:
            res=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM],issuer="expense-tracker")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401 , detail="invalid token")
        return int(res["sub"])


router=APIRouter(prefix="/auth")


@router.post("/login")
def login(user_info:connect_user,conn : Connection = Depends(get_db)):
    row=conn.execute(
        "select id,email,hashed_pass from users where email=%s ;",
        (user_info.email,)
    ).fetchone()
    if row is None : 
        raise HTTPException(status_code=401 , detail="failed to login ")
    
    if not bcrypt.checkpw(
        user_info.password.encode("utf-8"),
        row["hashed_pass"].encode("utf-8")
    ):
        raise HTTPException(status_code=401 , detail="failed to login ")
    payload={
        "sub" : str(row["id"]),
        "exp" : datetime.now(timezone.utc) + timedelta(minutes=15),
        "iss" : "expense-tracker"
    }    
    access_token=jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return {
            "access_token" : access_token,
            "token_type" : "bearer"
    }

@router.post("/register",status_code=201)
def register(user_info:connect_user ,conn : Connection = Depends(get_db)) -> create_user: 
    try:
        hashed_password = bcrypt.hashpw(
            user_info.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode()
        row=conn.execute(
            "insert into users (email,hashed_pass) values(%s,%s) returning id,email,created_at;",
            (user_info.email,hashed_password,),
        ).fetchone()
        conn.commit()
        return row
    except errors.UniqueViolation : 
        conn.rollback()
        raise HTTPException(status_code=409, detail="email already exist")
    except Exception:
        conn.rollback()
        raise


