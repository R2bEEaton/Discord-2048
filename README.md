# Discord-2048
A discord bot made in python for the game 2048 for Discord's Hack Week 2019.

**To test the bot, please join https://discord.gg/ADn4bx9**


**Game info:**
2048 is a game in which you must slide around tiles labeled with powers of 2 in four directions. When two tiles of the same value combine, they get added together, creating a new tile with double the value. After each successful move, a random tile either 2 or 4 is generated. The goal, as one might guess, is to reach a tile with a value of 2048. If at any point the user is unable to slide any tiles (the board is full and there are no adjacent combinations to be made) the game is over.

**Bot info:**
Python 3.6 or higher

Add a bot token in *bot_config.json* and choose either `true` or `false` for *"smoother"* which will determine if an await is added as a delay before adding in the random tile after each successful move (which, if true, makes it appear a bit smoother).

To use, type '!start' in a channel the bot has access to and it will start a game for you. You can control the direction you move by using the arrow reactions below the message. React a :regional_indicator_x: to end the game and remove the game board prematurely (only accessible by the user that started the game). Once the game ends in a win or loss, anyone can react a :regional_indicator_x: to remove the game board.

The encrypted text in the embed footer is game information like who originally requested the game and the actual state of the game. This is to prevent having to store each game's state in the bot program.
