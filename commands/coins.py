from main import *
import discord;
import modules.data as data

@group
class coins:
    @perms(permissions.is_admin)
    async def set(msg: discord.Message, piped, args):
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        if len(args) == 1:
            await msg.channel.send("Please provide a coin amount.")
            return
        user = parse_user(args[0])
        number = int(args[1])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        data.servers.write(msg.guild, f"coins.{user.id}", number)

        coinName = data.servers.read(msg.guild, "coins.name", "coin")
        await msg.channel.send(f"Set **{user.display_name}**'s {coinName} balance to {number}")

    @perms(permissions.is_admin)
    async def add(msg: discord.Message, piped, args):
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        if len(args) == 1:
            await msg.channel.send("Please provide a renicoin amount.")
            return
        user = parse_user(args[0])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        number = data.servers.read(msg.guild, f"coins.{user.id}", 0) + int(args[1])
        data.servers.write(msg.guild, f"coins.{user.id}", number)

        coinName = data.servers.read(msg.guild, "coins.name", "coin")
        await msg.channel.send(f"Set **{user.display_name}**'s {coinName} balance to {number}")

    async def get(msg: discord.Message, piped, args):
        if len(args) == 0:
            await msg.channel.send("Please provide a user mention or id.")
            return
        user = parse_user(args[0])

        if user is None:
            await msg.channel.send("That is not a valid user mention or id.")
            return

        number = data.servers.read(msg.guild, f"coins.{user.id}", 0)
        coinName = data.servers.read(msg.guild, "coins.name", "coin")
        await msg.channel.send(f"**{user.display_name}** has {number} {coinName}s.")