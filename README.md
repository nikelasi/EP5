# ΣP5
[![Python](https://img.shields.io/badge/Python-3.7.5-blue?logo=Python&logoColor=yellow&labelColor=blue&color=yellow&style=flat)](https://www.python.org/downloads/release/python-375/)
[![Sublime Text 3](https://img.shields.io/badge/Sublime%20Text-3-blue?logo=Sublime%20Text&logoColor=FF9800&labelColor=434343&color=FF9800&style=flat)](https://www.sublimetext.com/3)

![](assets/bot/banner_v1.png?raw=true)

EP5 is a discord bot made mainly to entertain me and my friends,
its sole purpose was for me to improve on an older bot of mine and
learn new libraries such as pymongo and asyncio. It was also created
so I can regularly practice programming while working on something
I find fun.

Throughout making this bot, I learnt various things such as,
performing database operations with mongodb, using heroku as a PaaS,
as well as other libraries. Besides, this also helped me better
understand the filesystem of a project and how to structure a project.

## Libraries

##### Bot & Async
[`discord.py`](https://pypi.org/project/discord.py/)
[`asyncio`](https://pypi.org/project/asyncio/)

##### Database
[`pymongo`](https://pypi.org/project/pymongo/)

##### Web
[`dnspython`](https://pypi.org/project/dnspython/)
[`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)
[`requests`](https://pypi.org/project/requests/)

##### Formatting
[`datetime`](https://pypi.org/project/DateTime/)

## Commands

#### User
Commands related to user data
e.g. stats, leaderboard,\
or something that contributes to the user data
e.g. prestige\
Regularly interacts with database mainly for reading
- [`stats`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/stats.md)
- [`leaderboard`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/leaderboard.md)
- [`prestige`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/prestige.md)

#### Economy
Includes commands to transfer money
or invest in the bank
- [`bank`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/bank.md)
- [`pay`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/pay.md)

#### Items
Items are almost like stocks where the prices
changes every 15 minutes randomly with a min
and max boundary defined in the database.
- [`backpack`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/backpack.md)
- [`shop`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/shop.md)
- [`buy`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/buy.md)
- [`sell`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/sell.md)
- [`price_change`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/price_change.md)
- [`gift`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/gift.md)

#### Rewards
Rewards is for new users to gain a small sum
of cash to get them started in the bot.\
Uses epoch time to keep track of when they last
claimed the rewards.
- [`hourly`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/rewards.md)
- [`daily`](https://github.com/NicholasJohansan/EP5/blob/main/docs/commands/rewards.md)

#### Fun
Some simple games whether for fun, or gambling,
up to the user.
- [`coinflip`](#)
- [`dice`](#)
- [`would_you_rather`](#)

#### Others
- [`collections`](#)

#### System
- [`ping`](#)
- [`prefix`](#)
- [`help`](#)