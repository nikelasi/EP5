# Leaderboard
[Back to User Commands](https://github.com/NicholasJohansan/EP5#user)

Fetches the `users` collection from mongodb and queries
for the all the users of the corresponding discord server as a parameter.

The data is then sorted accordingly to user balance by descending order,
provided there are more than 10 users on the server, it will only
return the Top 10 users.

Returns a list of not more than 10 users with their balance,
sorted in descending order according to their user balance

## Usage

`!leaderboard`\
Checks the leaderboard of the server
sorted according to balance

### Aliases
`ldb`
`lb`