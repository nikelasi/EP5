# Bank
[Back to Economy Commands](https://github.com/NicholasJohansan/EP5#economy)

Fetches the `users` collection from mongodb and queries
for the data using the user's ID as a parameter.

The bot will then parse the user data for their bank money
and the last time (in epoch time) they checked their bank
as well as their bank interest

It will then calculate the number of hourly iterations elapsed
and apply it to the compound interest formula, to get their
new balance and add it to the database.

## Usage

`!bank info`\
Checks the user's bank balance and interest

`!bank upgrade`\
Upgrades their bank interest by 1% provided the user has enough cash for the upgrade.\
The upgrades cost are calculated by an exponential function which takes into account their current interest rate.

`!bank withdraw <amount>`\
Withdraws <‌amount> from the user's bank balance into their user balance, provided they have <‌amount> in their bank balance

`!bank deposit <amount>`\
Deposits <‌amount> into the user's bank balance from their user balance, provided they have <‌amount> in their user balance