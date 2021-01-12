# Gift
[Back to Items Commands](https://github.com/NicholasJohansan/EP5#items)

Fetches the `items` collection from mongodb and queries
for the specified item that is going to be gifted.\
Does necessary checks to ensure that it is a validated transaction.\
Given everything is successful, the gift will then be processed

## Usage

`!gift @User <item-name>`\
Gifts @User 1 of <‌item-name>

`!gift @User <count> <item-name>`\
Gifts @User <‌count> of <‌item-name>