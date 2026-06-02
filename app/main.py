from fastapi import FastAPI, HTTPException
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

@app.put("/items/{item_id}")
def atualizar_item(item_id: int, nome: str):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item não encontrado")
    item.nome = nome
    db.commit()
    db.refresh(item)
    db.close()
    return item

@app.delete("/items/{item_id}")
def deletar_item(item_id: int):
    db = SessionLocal()
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        db.close()
        raise HTTPException(status_code=404, detail="Item não encontrado")
    db.delete(item)
    db.commit()
    db.close()
    return {"mensagem": f"Item {item_id} deletado com sucesso"}