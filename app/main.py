from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import time
import os

app = FastAPI()

DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:senha123@db:3306/appdb")

engine = create_engine(DB_URL)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

def wait_for_db():
    retries = 10
    while retries:
        try:
            engine.connect()
            print("Banco conectado!")
            return
        except Exception:
            print("Aguardando banco...")
            retries -= 1
            time.sleep(3)
    raise Exception("Banco não ficou disponível")

wait_for_db()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100))

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"mensagem": "FastAPI + MySQL + Docker + Azure = Projeto rodando! 🐳"}

@app.post("/items/")
def criar_item(nome: str):
    db = SessionLocal()
    item = Item(nome=nome)
    db.add(item)
    db.commit()
    db.refresh(item)
    db.close()
    return item

@app.get("/items/")
def listar_items():
    db = SessionLocal()
    items = db.query(Item).all()
    db.close()
    return items
