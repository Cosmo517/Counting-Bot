import os
import discord
from discord.ext import commands
import operator
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command(name='milestones', help='Lists # of numbers user typed')
async def milestones(ctx, start, end):
    counting_channel = discord.utils.get(ctx.guild.channels, name='counting')
    history_limit = start + end
    messages = [message async for message in counting_channel.history(limit=history_limit)]
    count_user_numbers = {}
    numbers_sent = []
    for x in messages:  # loop through all messages
        number_to_check = 0
        try:
            number_to_check = int(x.content)
        except ValueError:
            print("dead on: " + x.content)
            continue
        if int(end) >= number_to_check >= int(start):  # make sure its within bounds
            if number_to_check not in numbers_sent:  # check if we counted the number already
                numbers_sent.append(number_to_check)
                if x.author.name in count_user_numbers:
                    count_user_numbers[x.author.name] += 1
                else:
                    count_user_numbers[x.author.name] = 1

    final_message = f"Counting from {start} to {end}:\n\n"
    count_user_numbers = sorted(count_user_numbers.items(), key=operator.itemgetter(1), reverse=True)
    sum = 0
    for user in count_user_numbers:
        sum += user[1]
        final_message += f"{user[0]}: {user[1]}\n"

    print(final_message)
    print(f'Total sum: {sum}')
    await ctx.send(final_message)


must_restart = False


@bot.event
async def on_message(message):
    global must_restart
    # do not react to the bots output
    if message.author.name == bot.user.name:
        return

    # get the counting channel
    counting_channel = discord.utils.get(message.guild.channels, name='counting-restarts')

    # only get input from counting_channel
    if message.channel != counting_channel:
        return

    # remove a message if it contains words/not base 10
    try:
        int(message.content)
    except:
        await message.delete()
        await counting_channel.send("Restart! only base 10 numbers are allowed.")
        return



    # get the previous two messages
    messages = [message async for message in counting_channel.history(limit=2)]

    # check if messages[1] is the bots name
    # this means messages[0] should be 1
    if messages[1].author.name == bot.user.name:
        if int(messages[0].content) == 1:
            return
        else:
            await message.delete()
            await counting_channel.send("You must start at 1!")
    else:
        if int(messages[0].content) == int(messages[1].content) + 1:
            return
        else:
            await counting_channel.send("You must start at 1!")

bot.run(TOKEN)
