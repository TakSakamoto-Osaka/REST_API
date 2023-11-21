from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String
from sqlalchemy.ext.declarative import declarative_base

import uvicorn
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import BaseModel, parse_obj_as
from starlette.middleware.cors import CORSMiddleware


# SQLAlchemy 関連処理・定義
engine = create_engine("mysql+mysqldb://root:samurai@api-db:3306/api_demo?charset=utf8")
session = sessionmaker( bind=engine )()

Base = declarative_base()

class ItemModel(Base):
    __tablename__="item"
    
    ID      = Column(Integer, primary_key=True)
    Name    = Column(String(200))
    Price   = Column(Integer)
    Company = Column(String(200))
    Remarks = Column(String(500))


# Pydandic 関連処理・定義
class Item(BaseModel):
    ID:      int
    Name:    str
    Price:   int
    Company: str
    Remarks: str
    
    class Config:
        orm_mode = True


# FAST API処理
app = FastAPI()

# CORS対策設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

#
# TOPフォルダ
#
@app.get("/")
def top():
    return "Hello World"

#
# item データ取得
#
@app.get("/api/item/{id}", response_model=Item)
async def get_item(id: int):
    try:
        val = session.query(ItemModel).filter(ItemModel.ID == id).first()        # SQLAlchemy経由でDBからデータ取得
        item = parse_obj_as(Item,val)                                           # SQLAlchemyオブジェクトからPydanticオブジェクトに変換
   
        json_data = jsonable_encoder(item)
        
        session.commit()
    
        return JSONResponse(content=json_data)
    except:
        session.rollback()
    finally:
        if session is not None:
            session.close()
   

#
# item データリスト取得
#
@app.get("/api/items/{company}", response_model=List[Item])
async def get_items(company: str, all: bool = False):
    try:
        if all == True:
            list = session.query(ItemModel).all()
        else:
            list = session.query(ItemModel).filter(ItemModel.Company == company).all()
  
        items = parse_obj_as(List[Item], list)
  
        json_data = jsonable_encoder(items)
        session.commit()
    
        return JSONResponse(content=json_data)
    except:
        session.rollback()
    finally:
        if session is not None:
            session.close()

#
# item データ追加
#
@app.post("/api/item/")
async def post_item(item: Item):
    try:
        item_model         = ItemModel()
        
        item_model.Name    = item.Name
        item_model.Price   = item.Price
        item_model.Company = item.Company
        item_model.Remarks = item.Remarks
        
        session.add(item_model)
        session.commit()
    
        return JSONResponse(content='')
    except:
        session.rollback()
    finally:
        if session is not None:
            session.close()


#
# item データ変更
#
@app.put("/api/item/")
async def put_item(item: Item):
    try:
        id = item.ID
   
        val: ItemModel = session.query(ItemModel).filter(ItemModel.ID == id).first()
        
        if val is not None:
            val.Name    = item.Name
            val.Price   = item.Price
            val.Company = item.Company
            val.Remarks = item.Remarks
        
        session.commit()
    
        return JSONResponse(content='')
    except:
        session.rollback()
    finally:
        if session is not None:
            session.close()

#
# item データ削除:
#
@app.delete("/api/item/{id}")
async def delete_item(id: int):
    try:
        session.query(ItemModel).filter(ItemModel.ID == id).delete()
        session.commit()
    
        return JSONResponse(content='')
    except:
        session.rollback()
    finally:
        if session is not None:
            session.close()
   
    
if __name__=="__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8000)
