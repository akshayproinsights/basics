from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

import models
from database import engine, get_db

# Creates the 'rooms' table in rooms.db if it doesn't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# -----------------------------------------------
# Seed data — adds 5 rooms if table is empty
# -----------------------------------------------
def seed_data(db: Session):
    if db.query(models.Room).count() == 0:
        rooms = [
            models.Room(name="Deluxe Suite",     price=250, available=True),
            models.Room(name="Standard Room",    price=100, available=True),
            models.Room(name="Presidential",     price=500, available=False),
            models.Room(name="Economy Room",     price=60,  available=True),
            models.Room(name="Ocean View Suite", price=350, available=True),
        ]
        db.add_all(rooms)
        db.commit()


# -----------------------------------------------
# GET /rooms  →  return ALL rooms
# -----------------------------------------------
@app.get("/rooms")
def get_all_rooms(db: Session = Depends(get_db)):
    seed_data(db)
    rooms = db.query(models.Room).all()
    return {"rooms": rooms}


# -----------------------------------------------
# GET /rooms/{id}  →  return ONE room by ID
# -----------------------------------------------
@app.get("/rooms/{id}")
def get_room(id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {id} not found")
    return room


# -----------------------------------------------
# GET /rooms/filter/available  →  only available rooms
# -----------------------------------------------
@app.get("/rooms/filter/available")
def get_available_rooms(db: Session = Depends(get_db)):
    rooms = db.query(models.Room).filter(models.Room.available == True).all()
    return {"available_rooms": rooms}


# -----------------------------------------------
# POST /rooms  →  add a new room
# -----------------------------------------------
@app.post("/rooms")
def add_room(name: str, price: int, available: bool = True, db: Session = Depends(get_db)):
    new_room = models.Room(name=name, price=price, available=available)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)  # get the auto-generated ID back
    return {"message": "Room added!", "room": new_room}


# -----------------------------------------------
# PUT /rooms/{id}/book  →  book a room
# -----------------------------------------------
@app.put("/rooms/{id}/book")
def book_room(id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {id} not found")
    if not room.available:
        raise HTTPException(status_code=400, detail=f"Room {id} is already booked!")
    room.available = False
    db.commit()
    db.refresh(room)
    return {"message": f"Room {id} booked!", "room": room}


# -----------------------------------------------
# DELETE /rooms/{id}  →  delete a room
# -----------------------------------------------
@app.delete("/rooms/{id}")
def delete_room(id: int, db: Session = Depends(get_db)):
    room = db.query(models.Room).filter(models.Room.id == id).first()
    if not room:
        raise HTTPException(status_code=404, detail=f"Room {id} not found")
    db.delete(room)
    db.commit()
    return {"message": f"Room {id} deleted"}
