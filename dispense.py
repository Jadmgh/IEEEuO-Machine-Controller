import os
from fastapi import FastAPI, Request, Header
import httpx
import uvicorn
from pydantic import BaseModel

# import RPi.GPIO as GPIO
import time


RELAY_PINS = {
    1: 2,
    2: 3,
    3: 4,
    4: 17,
    5: 27,
    6: 22,
    7: 10,
    8: 9,
    9: 11,
    10: 5,
    11: 6,
    12: 13,
    13: 19,
    14: 26,
    15: 14,
    16: 15,
}


# GPIO.setmode(GPIO.BCM)
# for pin in RELAY_PINS.values():
#     GPIO.setup(pin, GPIO.OUT)
#     GPIO.output(pin, GPIO.HIGH)

app = FastAPI()
SQUARE_ACCESS_TOKEN
SQUARE_API_BASE = "https://connect.squareupsandbox.com/v2"
HEADERS = {
    "Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
    "Square-Version": "2025-07-16",
    "Content-Type": "application/json",
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


SLOT_RELAY = {
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
    "F4": [6, 7, 12, 13],
}


@app.post("/webhook/square")
async def handle_square_webhook(request: Request):
    payload = await request.json()
    print("Payload:", payload)
    print()
    event_type = payload.get("type")

    if event_type != "payment.updated":
        return {"message": "Ignoring non-payment update event"}

    payment = payload.get("data", {}).get("object").get("payment", {})
    status = payment.get("status")
    order_id = payment.get("order_id")

    if status != "COMPLETED" or not order_id:
        return {"message": "Ignoring non-completed payment or missing order ID"}

    async with httpx.AsyncClient() as client:
        # Fetch the full order
        order_url = f"{SQUARE_API_BASE}/orders/{order_id}"
        order_response = await client.get(order_url, headers=HEADERS)

        print(f"Fetching order {order_id} from Square API...")

        if order_response.status_code != 200:
            print(f"Error fetching order {order_id}: {order_response.text}")
            return {"message": "Error fetching order"}

        order_data = order_response.json()
        line_items = order_data.get("order", {}).get("line_items", [])

        print("Order data fetched successfully:", line_items)
        print(f"Order {order_id} fetched successfully. Processing line items...")

        for item in line_items:
            catalog_object_id = item.get("catalog_object_id")
            if not catalog_object_id:
                catalog_object_id = item.get("uid")
            if not catalog_object_id:
                print("No catalog object ID found for item:", item)
                continue

            # Fetch each item
            obj_url = f"{SQUARE_API_BASE}/catalog/object/{catalog_object_id}"
            obj_response = await client.get(obj_url, headers=HEADERS)

            print(obj_response)

            if obj_response.status_code == 200:
                object_data = obj_response.json()
                print(f"Custom attributes for {catalog_object_id}:", object_data)

                # Extract custom attributes dictionary
                custom_attrs = object_data["object"].get("custom_attribute_values", {})

                # Assume we’re only interested in the first custom attribute (can be generalized)
                if not custom_attrs:
                    print(f"No custom attributes found for {catalog_object_id}")
                    return

                first_attr = next(iter(custom_attrs.values()))
                selection_uid = first_attr["selection_uid_values"][0]
                definition_id = first_attr["custom_attribute_definition_id"]

                # Fetch the custom attribute definition
                definition_url = f"{SQUARE_API_BASE}/catalog/object/{definition_id}"
                definition_response = await client.get(definition_url, headers=HEADERS)

                print(
                    f"Fetching custom attribute definition {definition_id} for {catalog_object_id}..."
                )
                print(definition_response)

                if definition_response.status_code == 200:
                    definition = definition_response.json()
                    print(definition)
                    allowed_selections = definition["object"][
                        "custom_attribute_definition_data"
                    ]["selection_config"]["allowed_selections"]

                    # Find label for this selection UID
                    slot_label = next(
                        (
                            s["name"]
                            for s in allowed_selections
                            if s["uid"] == selection_uid
                        ),
                        None,
                    )

                    if slot_label:
                        print(f"Slot label for {catalog_object_id}: {slot_label}")
                        for pin in SLOT_RELAY.get(slot_label, []):
                            GPIO.output(RELAY_PINS[pin], GPIO.LOW)

                        time.sleep(3.3)

                        for pin in SLOT_RELAY.get(slot_label, []):
                            GPIO.output(RELAY_PINS[pin], GPIO.HIGH)
                    else:
                        print(f"Selection UID {selection_uid} not found in definition")

    return {"message": "Dispensing item from slot"}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
