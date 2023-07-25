import discord
import asyncio
import os

os.system("clear")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents = intents)

#region command prep crap

commands = {}

def command(func):
    print(f"Registered command {func.__name__}")
    commands[func.__name__] = func
    def wrapper(msg, piped, args, **kwargs):
        asyncio.run(func(msg, piped, args, **kwargs))
    return wrapper

@bot.event
async def on_message(msg : discord.Message):
    if(msg.content == ""
       or msg.author == bot.user
       or not msg.content.startswith(";")):
        return
    
    words = msg.content[1:].split(" ")
    cmd = ""
    args = []
    index = 0
    out = None
    error = False
    for word in words:
        if len(word) == 0 or word == " ":
            continue

        if cmd == "":
            cmd = word
        elif word != "|":
            args.append(word)

        index += 1

        if index == len(words) or word == "|":
            if not cmd in commands:
                error = True
                break
            out = await commands[cmd](msg, out, args)
            args = []
            cmd = ""

    if error:
        await msg.channel.send("That is not a command fool.")

#endregion

@command
async def echo(msg : discord.Message, piped, args):
    channel = msg.channel
    index = 0
    if args[0].startswith("<#"):
        index = 1
        channel = await bot.fetch_channel(args[0][2:-1])
    message = " ".join(args[index:])
    if piped is not None:
        message = piped
    await channel.send(message)
    
@command
async def ask(msg : discord.Message, piped, args):
    message = " ".join(args)
    if piped is not None:
        message = piped
    await msg.channel.send(message)
    return (await bot.wait_for("message", check=lambda m: m.channel == msg.channel)).content

bot.run(open("token").read())