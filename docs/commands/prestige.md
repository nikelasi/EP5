# Prestige
[Back to User Commands](https://github.com/NicholasJohansan/EP5#user)

Fetches the `users` collection from mongodb and queries
for the data using the user's ID as a parameter

Calculates the cost of the next prestige rank up and
states whether the user can rank up or not.

Provided the user has enough cash to rank up, they will
be prompted the option to.

Upon ranking up, their rewards multiplier will be increased by 0.75x
for each level of prestige rank, and the bot will subtract their
user balance by the cost to prestige.

## Usage

`!prestige`\
Manages the user prestige and derives rewards multiplier based on it.

### Aliases
`pres`