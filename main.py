from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Float, ForeignKey, select
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Literal
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- CONFIGURAÇÕES BÁSICAS ---
SECRET_KEY = "BANCO_SECURE_KEY"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- BANCO DE DADOS ASSÍNCRONO (SQLite) ---
engine = create_async_engine("sqlite+aiosqlite:///./banco.db")
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str] = mapped_column()
    balance: Mapped[float] = mapped_column(default=0.0)
    txs = relationship("Transaction", back_populates="owner")

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column() # "deposito" ou "saque"
    amount: Mapped[float] = mapped_column()
    date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="txs")

# --- ESQUEMAS DE VALIDAÇÃO (Pydantic) ---
class TransactionCreate(BaseModel):
    type: Literal["deposito", "saque"]
    amount: float = Field(..., gt=0, description="O valor deve ser positivo")

class TransactionOut(BaseModel):
    id: int
    type: str
    amount: float
    date: datetime
    class Config: from_attributes = True

class Statement(BaseModel):
    balance: float
    history: List[TransactionOut]

# --- DEPENDÊNCIAS E SEGURANÇA ---
async def get_db():
    async with async_session() as session: yield session

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username: raise HTTPException(status_code=401)
    except JWTError: raise HTTPException(status_code=401)
    
    res = await db.execute(select(User).where(User.username == username))
    user = res.scalar_one_or_none()
    if not user: raise HTTPException(status_code=401)
    return user

# --- API ---
app = FastAPI(title="Sistema Bancário RESTful")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)

@app.post("/register", status_code=201, tags=["Auth"])
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = User(username=username, password=pwd_context.hash(password))
    db.add(user); await db.commit()
    return {"msg": "Usuário criado"}

@app.post("/login", tags=["Auth"])
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).where(User.username == form.username))
    user = res.scalar_one_or_none()
    if not user or not pwd_context.verify(form.password, user.password):
        raise HTTPException(status_code=400, detail="Incorreto")
    token = jwt.encode({"sub": user.username, "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/transaction", tags=["Bank"])
async def create_tx(tx: TransactionCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if tx.type == "saque" and user.balance < tx.amount:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")
    
    user.balance += tx.amount if tx.type == "deposito" else -tx.amount
    new_tx = Transaction(type=tx.type, amount=tx.amount, user_id=user.id)
    db.add(new_tx); await db.commit()
    return {"msg": f"{tx.type} realizado", "new_balance": user.balance}

@app.get("/statement", response_model=Statement, tags=["Bank"])
async def get_statement(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Transaction).where(Transaction.user_id == user.id))
    return {"balance": user.balance, "history": res.scalars().all()}
