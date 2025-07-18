from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import RPi.GPIO as GPIO
import time

RELAY_PINS = {
    1: 2,   2: 3,   3: 4,   4: 17,
    5: 27,  6: 22,  7: 10,  8: 9,
    9: 11, 10: 5, 11: 6, 12: 13,
   13: 19, 14: 26, 15: 14, 16: 15
}


GPIO.setmode(GPIO.BCM)
for pin in RELAY_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)
    
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

SLOT_RELAY= {
    "A1": [3, 12, 13, 14],
    "A2": [3, 7, 13, 14],
    "A3": [3, 7, 12, 14],
    "A4": [3, 7, 12, 13],

    "B1": [2, 12, 13, 14],
    "B2": [2, 7, 13, 14],
    "B3": [2, 7, 12, 14],
    "B4": [2, 7, 12, 13],

    "C1": [5, 12, 13, 14],
    "C2": [5, 7, 13, 14],
    "C3": [5, 7, 12, 14],
    "C4": [5, 7, 12, 13],

    "F1": [6, 12, 13, 14],
    "F2": [6, 7, 13, 14],
    "F3": [6, 7, 12, 14],
    "F4": [6, 7, 12, 13]
}

class Item(BaseModel):
    slot: str

@app.post("/dispense")
async def dispense_item(item: Item):
    for pin in SLOT_RELAY.get(item.slot):
        GPIO.output(RELAY_PINS[pin], GPIO.LOW)
        
    time.sleep(3.3)

    for pin in SLOT_RELAY.get(item.slot):
        GPIO.output(RELAY_PINS[pin], GPIO.HIGH)
        
    
    return {"message": f"Dispensing item from {item.slot}"}

if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")