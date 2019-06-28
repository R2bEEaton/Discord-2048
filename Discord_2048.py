import discord
import base91
import numpy as np
from random import randint
import json

with open('bot_config.json') as json_data_file:
    data = json.load(json_data_file)

TOKEN = data["token"]
# If smoother is specified in the config file, it awaits before sending the new random tile, making it slightly more smoothe
smoother = data["smoother"]

dbot = discord.Client()
numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def array_to_string(array_in, user):
    string = ""
    string2 = ""
    rows = array_in.shape[0]
    cols = array_in.shape[1]

    for x in range(0, rows):
        for y in range(0, cols):
            string += str(array_in[x][y]).replace(".0", "")
            for i in range(0, len(str(np.amax(array_in)).replace(".0", "")) - len(
                    str(array_in[x][y]).replace(".0", ""))):
                string2 += ":new_moon:"
            for char in str(array_in[x][y]).replace(".0", ""):
                if char == "0" and str(array_in[x][y]).replace(".0", "") == "0":
                    string2 += ":new_moon:"
                else:
                    string2 += ":" + numbers[int(char)] + ":"
            if y != 3:
                string += ","
                if len(str(np.amax(array_in)).replace(".0", "")) > 1:
                    string2 += ":tm:"
                else:
                    string2 += "   "
        if x != 3:
            string += "|"
            string2 += "\n"
            for i in range(0, len(str(np.amax(array_in)).replace(".0", ""))):
                string2 += "\n"

    # Adds user id so the next action can tell who the game belongs to
    string += "[]%s" % user

    # Returns string2 as well which is the emoji-fied version of the game board
    return string, string2


def string_to_array(string):
    # Turn the string from the footer back into a numpy array that can be acted upon
    output = np.zeros((4, 4))
    x_num = 0
    y_num = 0
    for x in string.split("[]")[0].split("|"):
        for y in x.split(","):
            output[x_num][y_num] = y
            y_num += 1
        y_num = 0
        x_num += 1
    user = string.split("[]")[1]

    # Returns output array and original game user
    return output, user


async def delete_game(reaction):
    await reaction.message.edit(content="*Game removed*", embed=None)
    for emoji in ['⬆', '⬇', '⬅', '➡']:
        await reaction.message.remove_reaction(emoji=emoji, member=dbot.user)
    await reaction.message.remove_reaction(emoji=reaction, member=dbot.user)


def check_valid(output2):
    # Check for valid moves
    rows = output2.shape[0]
    cols = output2.shape[1]
    found = False
    original = output2

    for j in range(0, 4):
        output2 = np.zeros(shape=(4, 4))
        output = original
        output = np.rot90(output, j)
        # Move everything to the left 4 times to be sure to get everything
        for i in range(0, 3):
            output2 = np.zeros(shape=(4, 4))
            for x in range(0, cols):
                for y in range(0, rows):
                    if y != 0:
                        if output[x][y - 1] == 0:
                            output2[x][y - 1] = output[x][y]
                        else:
                            output2[x][y] = output[x][y]
                    else:
                        output2[x][y] = output[x][y]
            output = output2

        # Combine adjacent equal tiles
        output3 = np.zeros(shape=(4, 4))
        for x in range(0, cols):
            for y in range(0, rows):
                if y != 0:
                    if output2[x][y - 1] == output2[x][y]:
                        output3[x][y - 1] = output2[x][y] * 2
                    else:
                        output3[x][y] = output2[x][y]
                else:
                    output3[x][y] = output2[x][y]

        output = output3

        # Move over two more times
        for i in range(0, 1):
            output3 = np.zeros(shape=(4, 4))
            for x in range(0, cols):
                for y in range(0, rows):
                    if y != 0:
                        if output[x][y - 1] == 0:
                            output3[x][y - 1] = output[x][y]
                        else:
                            output3[x][y] = output[x][y]
                    else:
                        output3[x][y] = output[x][y]
            output = output3

        output2 = output3
        output2 = np.rot90(output2, 4-j)

        if np.array_equal(original, output2) is False:
            found = True

    if found is True:
        return True
    else:
        return False


@dbot.event
async def on_message(message):
    if message.author == dbot.user:
        return

    if message.content.startswith('!start'):
        # To show who's game it is (no one else can play the game than this person)
        e = discord.Embed(title="%s's Game!" % message.author)

        # Generate Random Game Board
        start_array = np.zeros(shape=(4, 4))

        first = randint(0, 3)
        second = randint(0, 3)
        start_array[first][second] = randint(1, 2) * 2

        found = False
        while found is not True:
            first_2 = randint(0, 3)
            second_2 = randint(0, 3)
            if first_2 == first and second_2 == second:
                None
            else:
                found = True
                start_array[first_2][second_2] = randint(1, 2) * 2

        #start_array[randint(0, 3)][randint(0, 3)] = randint(1, 90) * 2

        string, string2 = array_to_string(start_array, message.author.mention)

        e.add_field(name="Try to get the 2048 tile!", value=string2)
        e.set_footer(text=base91.encode(bytes(string, 'utf-8')))

        new_msg = await message.channel.send(embed=e)
        print(start_array)
        # Add control reactions
        for emoji in ['⬆', '⬇', '⬅', '➡']:
            await new_msg.add_reaction(emoji)


@dbot.event
async def on_reaction_add(reaction, user):
    # Stop the bot from going when it adds its own reactions
    if user == dbot.user:
        return

    # Just to show in the console which reaction is being sent
    print(reaction)

    # If the message that was reacted on was one sent by the bot, guaranteeing it's a game
    if reaction.message.author == dbot.user:
        # Game is over and anyone can delete the game board and reactions by reacting the X emoji
        if reaction.emoji == '🇽' and base91.decode(reaction.message.embeds[0].footer.text).decode("utf-8") == "Game over!":
            await delete_game(reaction)
        else:
            # decode footer from base91
            footer = base91.decode(reaction.message.embeds[0].footer.text).decode("utf-8")
            output, user2 = string_to_array(footer)

            # if the user is the same one that started the game
            if user2 == user.mention:
                original = output

                rows = output.shape[0]
                cols = output.shape[1]
                output2 = np.zeros(shape=(4, 4))

                if reaction.emoji == '🇽':
                    # Game is still going and original user can decide to delete game
                    await delete_game(reaction)
                    await reaction.message.remove_reaction(emoji=reaction, member=user)
                    return
                # Rotate arrays to all be facing to the left to make actions on them easier
                elif reaction.emoji == '⬅':
                    output = np.rot90(output, 0)
                elif reaction.emoji == '➡':
                    output = np.rot90(output, 2)
                elif reaction.emoji == '⬆':
                    output = np.rot90(output, 1)
                elif reaction.emoji == '⬇':
                    output = np.rot90(output, 3)
                else:
                    await reaction.message.remove_reaction(emoji=reaction, member=user)
                    return

                # Move everything to the left 4 times to be sure to get everything
                for i in range(0, 3):
                    output2 = np.zeros(shape=(4, 4))
                    for x in range(0, cols):
                        for y in range(0, rows):
                            if y != 0:
                                if output[x][y-1] == 0:
                                    output2[x][y-1] = output[x][y]
                                else:
                                    output2[x][y] = output[x][y]
                            else:
                                output2[x][y] = output[x][y]
                    output = output2

                # Combine adjacent equal tiles
                output3 = np.zeros(shape=(4, 4))
                for x in range(0, cols):
                    for y in range(0, rows):
                        if y != 0:
                            if output2[x][y - 1] == output2[x][y]:
                                output3[x][y - 1] = output2[x][y]*2
                                output2[x][y] = 0
                            else:
                                output3[x][y] = output2[x][y]
                        else:
                            output3[x][y] = output2[x][y]

                output = output3

                # Move over two more times and check if the board has a 2048 in it or if it's completely full
                found_win = False
                found_end = True
                for i in range(0, 1):
                    output3 = np.zeros(shape=(4, 4))
                    for x in range(0, cols):
                        for y in range(0, rows):
                            if y != 0:
                                if output[x][y-1] == 0:
                                    output3[x][y-1] = output[x][y]
                                else:
                                    output3[x][y] = output[x][y]
                            else:
                                output3[x][y] = output[x][y]
                            if output3[x][y] == 2048:
                                found_win = True
                            if output3[x][y] == 0:
                                found_end = False
                    output = output3

                output2 = output3

                e = discord.Embed(title="%s's Game!" % user)

                # Undo the rotations from before
                if reaction.emoji == '⬅':
                    output2 = np.rot90(output2, 0)
                if reaction.emoji == '➡':
                    output2 = np.rot90(output2, 2)
                if reaction.emoji == '⬆':
                    output2 = np.rot90(output2, 3)
                if reaction.emoji == '⬇':
                    output2 = np.rot90(output2, 1)

                # If there's a 2048 on the board, the player won! Add the win gif
                if found_win is True:
                    e = discord.Embed()
                    e.add_field(name="%s got the 2048 tile!" % user, value="You did it!!")
                    e.set_image(url="https://media1.giphy.com/media/l2SpR4slaePsGG49O/giphy.gif")
                    e.set_footer(text=base91.encode(b"Game over!"))
                    await reaction.message.edit(embed=e)
                    for emoji in ['⬆', '⬇', '⬅', '➡']:
                        await reaction.message.remove_reaction(emoji=emoji, member=dbot.user)
                    await reaction.message.add_reaction('🇽')
                # If the array changed from how it was before and if there are any empty spaces on the board, add a random tile
                elif np.array_equal(output2, original) is False and found_end is False:
                    if smoother == False:
                        found = False
                        while found is not True:
                            first_2 = randint(0, 3)
                            second_2 = randint(0, 3)
                            if output2[first_2][second_2] == 0:
                                found = True
                                output2[first_2][second_2] = randint(1, 2) * 2

                    string, string2 = array_to_string(output2, user.mention)

                    print(string)

                    e.add_field(name="Try to get the 2048 tile!", value=string2)
                    e.set_footer(text=base91.encode(bytes(string, 'utf-8')))
                    await reaction.message.edit(embed=e)

                    # Check if there are valid moves and if not, end the game
                    if check_valid(output2) is False:
                        print("end")
                        # If there are no 0's, check if there are any valid moves. If there aren't, say the game is over.
                        e = discord.Embed()
                        e.add_field(name="%s is unable to make any more moves." % user, value=":cry:")
                        e.set_image(url="https://media2.giphy.com/media/joNVQCtuecqHK/giphy.gif")
                        e.set_footer(text=base91.encode(b"Game over!"))
                        await reaction.message.edit(embed=e)
                        for emoji in ['⬆', '⬇', '⬅', '➡']:
                            await reaction.message.remove_reaction(emoji=emoji, member=dbot.user)
                        await reaction.message.add_reaction('🇽')

                    if smoother == True:
                        found = False
                        while found is not True:
                            first_2 = randint(0, 3)
                            second_2 = randint(0, 3)
                            if output2[first_2][second_2] != 0:
                                None
                            else:
                                found = True
                                output2[first_2][second_2] = randint(1, 2) * 2

                        string, string2 = array_to_string(output2, user.mention)
                        e = discord.Embed()
                        e.add_field(name="Try to get the 2048 tile!", value=string2)
                        e.set_footer(text=base91.encode(bytes(string, 'utf-8')))
                        await reaction.message.edit(embed=e)
                elif check_valid(output2) is False:
                    print("end")
                    # If there are no 0's, check if there are any valid moves. If there aren't, say the game is over.
                    e = discord.Embed()
                    e.add_field(name="%s is unable to make any more moves." % user, value=":cry:")
                    e.set_image(url="https://media2.giphy.com/media/joNVQCtuecqHK/giphy.gif")
                    e.set_footer(text=base91.encode(b"Game over!"))
                    await reaction.message.edit(embed=e)
                    for emoji in ['⬆', '⬇', '⬅', '➡']:
                        await reaction.message.remove_reaction(emoji=emoji, member=dbot.user)
                    await reaction.message.add_reaction('🇽')
                else:
                    print("else")
                    # They made a valid move, but it didn't change anything, so don't add a new tile
                    string, string2 = array_to_string(output2, user.mention)

                    print(string)

                    e.add_field(name="Try to get the 2048 tile!", value=string2)
                    e.set_footer(text=base91.encode(bytes(string, 'utf-8')))
                    await reaction.message.edit(embed=e)

        # Remove reaction
        await reaction.message.remove_reaction(emoji=reaction, member=user)


@dbot.event
async def on_ready():
    print('Logged in as')
    print(dbot.user.name)
    print(dbot.user.id)
    print("Bot made by R2bEEaton.")
    print('------')

dbot.run(TOKEN)