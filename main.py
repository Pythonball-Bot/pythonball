import discord
import asyncio
import os
from PIL import Image
import modules.data as data
from modules.commands import commands, groups
import commands.board as board
import importlib

os.system("clear")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = discord.Client(intents = intents)

# testy = bot.get_guild(717048644708073534)

afkMessages = []

@bot.event
async def on_message(msg : discord.Message):
    if(msg.content == ""
       or msg.author == bot.user):
        return
    
    for i, afkMessage in enumerate(afkMessages):
        if msg.author.id == afkMessage["user"]:
            await msg.channel.send("hi welcome back")
            afkMessages.pop(i)
            break
    
    for mention in msg.mentions:
        for i, afkMessage in enumerate(afkMessages):
            if msg.guild.id != afkMessage["server"]: continue
            if mention.id != afkMessage["user"]: continue
            await msg.channel.send(afkMessage["message"])

    if not msg.content.startswith(";"): return

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
            cmd = word.lower()
        elif word != "|":
            args.append(word)

        index += 1

        if index == len(words) or word == "|":
            if cmd.lower() in groups:
                cmd = f"{cmd}.{args[0].lower()}"
                args.pop(0)
            if not cmd in commands["functions"].keys():
                error = True
                break
            try:
                canRun = True
                if cmd in commands["permissions"].keys():
                    for perm in commands["permissions"][cmd]:
                        if not perm(msg.author):
                            await msg.channel.send(f"Missing required permission: {perm.__name__}")
                            canRun = False
                if canRun: out = await commands["functions"][cmd](bot, msg, out, args)
            except IndexError:
                await msg.channel.send("Missing required paramters.")
                await msg.add_reaction("🚫")
            args = []
            cmd = ""

    if error:
        await msg.channel.send("That is not a command fool.")

@bot.event
async def on_raw_reaction_add(event : discord.RawReactionActionEvent):
    message = await (await bot.fetch_channel(event.channel_id)).fetch_message(event.message_id)
    user = await bot.fetch_user(event.user_id)
    for reaction in message.reactions:
        if reaction.emoji == event.emoji:
            await board.board_check(bot, reaction, user)

if __name__ == "__main__":
    for file in os.listdir("commands"):
        if not file.endswith(".py"): continue
        importlib.import_module(f"commands.{file[:-3]}")
    bot.run(open("SECRET/token").read())