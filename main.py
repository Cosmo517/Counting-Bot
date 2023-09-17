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
    if message.author.name == bot.user.name:
        return

    try:
        int(message.content)
    except:
        await message.delete()
        return

    counting_channel = discord.utils.get(message.guild.channels, name='counting-restarts')
    messages = [message async for message in counting_channel.history(limit=2)]
    if int(messages[1].content) == (int(messages[0].content) + 1) and must_restart is not False:
        return
    elif must_restart:
        print(f'must_restart: {must_restart}, message: {message}')
        await message.delete()
        await counting_channel.send("You must start at 1!")
    else:
        print(f'must_restart: {must_restart}, message: {message}')
        await message.delete()
        must_restart = True
        await counting_channel.send("Restart!")


bot.run(TOKEN)
