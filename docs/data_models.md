# Data Models
This is a collection of the data models used for the database in mongodb.

### User

```json
data = {
	"_id": "{guild_id}-{user_id}",
	"money": 0,
	"bank": {
		"money": 0,
		"interest": 0.01,
		"last_seen": 0
	},
	"rewards": {
		"daily": 0,
		"hourly": 0
	},
	"prestige": 0
}
```
ID: {Guild_ID}-{User_ID} -> User Identification\
Money -> User Balance\
Prestige -> User Prestige Rank (-1)\

Bank.Money -> User Bank Balance\
Bank.Interest -> User Bank Hourly Compound Interest Rate\
Bank.Last_Seen -> The last time the user accessed the bank in unix time\

Rewards.Daily -> Last collection time of daily reward in unix time\
Rewards.Hourly -> Last collection time of hourly reward in unix time\

### Item
```json
data = {
	"server_id": "{guild_id}",
	"name": "item",
	"cost": 10,
	"max": 20,
	"supply": null,
	"description": "",
	"owners": {
		"123456789": 20,
		"123456543": 10,
		"734565234": 1
	},
	"avg_price": 25,
	"multipliers": [0, 100]
}
```
Server_ID -> The server which the item belongs to\
Name -> Name of item\
Cost -> Current cost of item\
Max -> Maximum amount of the item that can be owned\
Supply -> Amount of supply; null if infinite supply\
Description -> Description of item\
Avg_Price -> Average price of item\
Multipliers -> Array [min_percentage, max_percentage] -> price of item can range from min_percentage * avg price to max_percentage * avg_price when prices are changed every 15 minutes\
Owners -> Dictionary of owners in key-value pairs where key is UserID and value is Amount Owned\



