# Pay
[Back to Economy Commands](https://github.com/NicholasJohansan/EP5#economy)

Fetches the `users` collection from mongodb and queries
for the data using the user's ID as a parameter.\
And also queries for the user data of the person that the user is sending the cash to

Some checks will be done to ensure that there is no loopholes
and the payment will be made afterwards, and the database will be updated

## Usage

`!pay @User <amount>`\
Pays @User <‌amount> Σ, provided the user has <‌amount> of cash.

### Aliases
`send`