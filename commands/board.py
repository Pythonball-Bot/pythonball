from main import bot
from modules.commands import *
import modules.data as data
import discord
import datetime
import re

@group
class board:
    async def add(msg: discord.Message, piped, args):
        if not msg.author.guild_permissions.administrator: return
        await msg.channel.send("What is the emoji for this board?")
        emoji = (await bot.wait_for("message", check=lambda m: m.channel == msg.channel and m.author == msg.author)).content
        if(len(emoji) > 1):
            await msg.channel.send("Either you forgot a space or you sent a custom emoji. Custom emoji boards aren't supported yet, until they are you have to use built in emojis.")
            return
        
        await msg.channel.send("What channel should this board's messages be sent to?")
        channel = (await bot.wait_for("message", check=lambda m: m.channel == msg.channel and m.author == msg.author)).content

        await msg.channel.send("What board type is it?\n**super** : Every member can put any message on the board with one react, but only every <n> hours\n**threshold** : A message goes to the board if it gets <n> total reactions")
        type = (await bot.wait_for("message", check=lambda m: m.channel == msg.channel and m.author == msg.author)).content

        await msg.channel.send("How many hours is the super react cooldown?" if type == "super" else "How many reacts does a message need?")
        count = int((await bot.wait_for("message", check=lambda m: m.channel == msg.channel and m.author == msg.author)).content)

        index = len(data.servers.read(msg.guild, "boards", {}).keys())
        if type == "super": data.servers.write(msg.guild, f"boards.{index}", {"type": "super", "channel": int(channel[2:-1]), "count": count, "lastReactions": {}, "emoji": emoji})
        else: data.servers.write(msg.guild, f"boards.{index}", {"type": "threshold", "channel": int(channel[2:-1]), "count": count, "emoji": emoji})
        await msg.channel.send(f"Board created!")

    # async def force(msg: discord.Message, piped, args):
    #     if msg.author.guild_permissions.manage_messages is False and msg.author.id != owner:
    #         await msg.channel.send("Manage Messages is required to use this command.")
    #         return
        
    #     server_check(msg.guild.id)
    #     if len(args) == 0:
    #         await msg.channel.send("Please specify a board to add the message to (with the emoji of that board)")
    #         return
    #     emoji = args[0]
    #     message = msg.reference
    #     if message is None:
    #         if len(args) < 2:
    #             await msg.channel.send("Either reply to a message or add the message ID after the emoji, otherwise I don't know what message to add.")
    #             return
    #         message = await msg.channel.fetch_message(int(args[1]))
    #     if not emoji in servers[str(msg.guild.id)]["boards"]:
    #         await msg.channel.send(f"There is no {emoji} board in the server.")
    #         return
        
    #     boar = servers[str(msg.guild.id)]["boards"][emoji]
    #     await add_to_board(boar, message, emoji)
    #     await msg.channel.send(f"Added the messgage to the {emoji} board.")


async def add_to_board(index, message):
    if type(message) == discord.MessageReference:
        message = await (bot.get_guild(message.guild_id).get_channel(message.channel_id)).fetch_message(message.message_id)

    boar = data.servers.read(message.guild, f"boards.{index}")
    async with (await bot.fetch_channel(boar["channel"])).typing():
        boar["messages"].append(message.id)
        data.servers.write(message.guild, f"boards.{index}.messages", boar["messages"])
        embed = discord.Embed(description = message.content)
        match = re.match(r"^https:\/\/[\w\.]*\/[\w\-\/]+\.(?:png|gif)(?!\.).*", message.content)
        if match is not None:
            embed.set_image(url = match.string)
        if len(message.attachments) > 0:
            embed.set_image(url = message.attachments[0].url)
        if message.content.startswith("https://") and "tenor.com" in message.content:
            embed.set_image(url = message.content)
        embed.set_author(name = message.author.name, icon_url = message.author.avatar.url)
        embed.timestamp = message.created_at
        number = len(message.attachments) - 1
        embed.set_footer(text = f"+ {number} more attachment{'s' if number > 1 else ''}" if number > 0 else None)
        await (await bot.fetch_channel(boar["channel"])).send(f"{boar['emoji']} {message.jump_url}", embed = embed)

@bot.event
async def on_reaction_add(reaction : discord.Reaction, user : discord.Member):
    server = user.guild.id
    for i, boar in enumerate(data.servers.read(reaction.message.guild, "boards", {})):
        if reaction.emoji != boar["emoji"]: continue
        if boar["type"] == "super":
            if str(user.id) not in boar["lastReactions"]: lastReaction = 0
            else: lastReaction = datetime.datetime.fromisoformat(
                boar["lastReactions"][str(user.id)])
            secondsSinceReact = (datetime.datetime.now() - lastReaction).seconds
            if secondsSinceReact < boar["count"] * 60 * 60:
                if not reaction.message.id in boar["messages"]:
                    await add_to_board(i, reaction.message, reaction.emoji)
                    data.servers.write(reaction.message.guild, f"boards.{i}.lastReactions.{str(user.id)}", datetime.datetime.now().isoformat())
        if boar["type"] == "threshold":
            if reaction.count >= boar["count"]:
                if not reaction.message.id in boar["messages"]:
                    await add_to_board(i, reaction.message)