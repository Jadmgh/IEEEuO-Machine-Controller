package main

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stianeikeland/go-rpio/v4"
)

type item struct {
	Slot string `json:"slot"`
}

func dispenseItem(c *gin.Context) {

	SLOT_RELAY := map[string][]rpio.Pin{
		"A1": {3, 12, 13, 14},
		"A2": {3, 7, 13, 14},
		"A3": {3, 7, 12, 14},
		"A4": {3, 7, 12, 13},

		"B1": {2, 12, 13, 14},
		"B2": {2, 7, 13, 14},
		"B3": {2, 7, 12, 14},
		"B4": {2, 7, 12, 13},

		"C1": {5, 12, 13, 14},
		"C2": {5, 7, 13, 14},
		"C3": {5, 7, 12, 14},
		"C4": {5, 7, 12, 13},

		"F1": {6, 12, 13, 14},
		"F2": {6, 7, 13, 14},
		"F3": {6, 7, 12, 14},
		"F4": {6, 7, 12, 13},
	}

	//Create an item struct from the JSON received by the endpoint
	var newItem item
	if err := c.BindJSON(&newItem); err != nil {
		return
	}

	//Activate the necessary relays to make the motor spin
	for _, pin := range SLOT_RELAY[newItem.Slot] {
		pin.Low()
	}

	time.Sleep(3300 * time.Millisecond)

	for _, pin := range SLOT_RELAY[newItem.Slot] {
		pin.High()
	}

	c.IndentedJSON(http.StatusCreated, "Dispensing item from "+newItem.Slot)

}

func getRoot(c *gin.Context) {
	c.IndentedJSON(http.StatusOK, "Hello, World")
}

func main() {
	RELAY_PINS := map[int]rpio.Pin{
		1: rpio.Pin(2), 2: rpio.Pin(3), 3: rpio.Pin(4), 4: rpio.Pin(17),
		5: rpio.Pin(27), 6: rpio.Pin(22), 7: rpio.Pin(10), 8: rpio.Pin(9),
		9: rpio.Pin(11), 10: rpio.Pin(5), 11: rpio.Pin(6), 12: rpio.Pin(13),
		13: rpio.Pin(19), 14: rpio.Pin(26), 15: rpio.Pin(14), 16: rpio.Pin(15),
	}

	//Initialize the pins
	for _, pin := range RELAY_PINS {
		pin.Output()
		pin.High()
	}

	//Initialize the API endpoints
	router := gin.Default()
	router.GET("/", getRoot)
	router.POST("/dispense", dispenseItem)

	router.Run("0.0.0.0:8000")
}
