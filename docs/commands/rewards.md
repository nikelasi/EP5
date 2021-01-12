# Rewards
[Back to Reward Commands](https://github.com/NicholasJohansan/EP5#rewards)

Queries the `users` collection from mongodb to check when
users last collected their respective rewards.\
Time is given in epoch time for easier calculations.

All rewards commands are handled by the same rewards handler,
the only differing areas amongst rewards commands are:\
~ Time Period (Claimed every ?)\
~ Reward Range (1 ~ ? Cash)

If the user is above Prestige Rank 1,
there will be a rewards multiplier of
0.75x applied for every subsequent Prestige Rank

The bot will then add the reward sum to the user's balance

## Usage

`!hourly`\
Hourly rewards of 1 to 20 cash.

`!daily`\
Daily rewards of 1 to 300 cash