import discord
import asyncio
import os
from PIL import Image
import modules.data
import modules.commands as commands
import importlib

owner = 663186731725488138
subowners = [993927156142981240, 993927897477828790]

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
            if cmd.lower() in commands.groups:
                cmd = f"{cmd}:{args[0].lower()}"
                args.pop(0)
            if not cmd in commands.cmds:
                error = True
                break
            try:
                for perm in commands.cmds[cmd.lower()]["permissions"]:
                    if not perm(msg.author):
                        await msg.channel.send(f"Missing required permission: {perm.__name__}")
                        break
                out = await commands.cmds[cmd.lower()]["function"](msg, out, args)
            except IndexError:
                await msg.channel.send("Missing required paramters.")
                await msg.add_reaction("🚫")
            args = []
            cmd = ""

    if error:
        await msg.channel.send("That is not a command fool.")

# @bot.event
# async def on_reaction_add(reaction : discord.Reaction, user : discord.Member):
#     server = user.guild.id
#     server_check(server)
#     if reaction.emoji in servers[str(server)]["boards"].keys():
#         boar = servers[str(server)]["boards"][reaction.emoji]
#         if reaction.count >= boar["count"]:
#             if not reaction.message.id in boar["messages"]:
#                 await add_to_board(boar, reaction.message, reaction.emoji)

if __name__ == "__main__":
    for file in os.listdir("commands"):
        if not file.endswith(".py"): continue
        importlib.import_module(f"commands.{file[:-3]}")
    bot.run(open("SECRET/token").read())