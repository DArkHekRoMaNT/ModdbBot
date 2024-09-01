import asyncio
import logging
import os
import traceback
from datetime import datetime
from queue import Queue
from typing import Optional, Literal

import discord
from discord import Message, app_commands, Interaction, Forbidden
from discord.app_commands import AppCommandError
from discord.ext import commands, tasks

from . import api
from .api.models import *
from .subscription import SubscribedUser, SubscriptionManager

logger = logging.getLogger("discord_bot")

_comment_queue = Queue[(int, Comment)]()
_notify_queue = Queue[str]()


def send_comment(user_id: int, comment: Comment):
    _comment_queue.put((user_id, comment))


def send_notify(msg: str):
    _notify_queue.put(msg)


def run(token: str, subs: SubscriptionManager):
    while True:
        try:
            logger.info("Start")
            _run_internal(token, subs)
            logger.info("Stop")
        except Exception as e:
            logger.error(e.__str__())
            logger.info("Re-running")


def _run_internal(token: str, subs: SubscriptionManager):
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='/', intents=intents, owner_id=int(os.getenv("MY_DISCORD_USER_ID")))

    @bot.event
    async def on_ready():
        await send_notify_message(title="Ready")
        await loop.start()

    @bot.event
    async def on_message(message: Message):
        if message.author.id == bot.user.id:
            return

        await bot.process_commands(message)
        logger.info(message.content)

    async def on_error(interaction: Interaction, error: AppCommandError):
        error_msg = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        await send_notify_message(
            msg=error_msg,
            title="Error",
            extra_first_field_name="User",
            extra_first_field_value=f"<@{interaction.user.id}>",
            critical=True)

    @tasks.loop(seconds=10)
    async def loop():
        while _comment_queue.qsize() > 0:
            user_id, comment = _comment_queue.get()
            user = await bot.fetch_user(user_id)
            if not user.dm_channel:
                await user.create_dm()
            await user.dm_channel.send(embed=get_embed(comment))
        while _notify_queue.qsize() > 0:
            await send_notify_message(title=_notify_queue.get())

    def get_embed(comment: Comment) -> discord.Embed:
        mod = api.get_mod_by_asset_id(comment.asset_id)
        user = api.get_author(comment.user_id)
        link = f"https://mods.vintagestory.at/show/mod/{mod.asset_id}#cmt-{comment.comment_id}"
        embed = discord.Embed(title="New message!", url=link, color=0x42bea8, timestamp=comment.created)
        embed.add_field(name=user.name, value=comment.text[:1024], inline=False)
        embed.set_footer(text=f"{mod.name}")
        return embed

    @bot.tree.command(name="set_user", description="Set your moddb user name")
    @app_commands.describe(name="Your moddb user name")
    async def set_user(interaction: Interaction, name: str):
        moddb_user = api.search_author(name, case_sensitive=False)
        if not moddb_user:
            await interaction.response.send_message(f"Unknown user {name}", ephemeral=True, delete_after=30)
            return
        user = subs.get_user(discord_user_id=interaction.user.id)
        user.moddb_user_id = moddb_user.user_id
        user.moddb_name_cached = moddb_user.name
        subs.update_user(user)
        await interaction.response.send_message(f"Subscribed to user {moddb_user.name}", ephemeral=True, delete_after=30)

    @bot.tree.command(name="autohide_logs", description="Any detected logs/crashlogs will be removed")
    async def hide_logs(interaction: Interaction, enabled: bool):
        user = subs.get_user(interaction.user.id)
        user.skip_logs = enabled
        subs.update_user(user)
        await interaction.response.send_message("Hide logs now" if enabled else "Show logs now", ephemeral=True, delete_after=30)

    @bot.tree.command(name="reset", description="Reset all settings")
    async def reset_all(interaction: Interaction):
        subs.update_user(SubscribedUser(dict({"discord_user_id": interaction.user.id})))
        await interaction.response.send_message(f"All settings removed", ephemeral=True, delete_after=30)

    @bot.command()
    @commands.is_owner()
    async def cls(interaction: Interaction, limit: int = 100):
        await interaction.response.send_message(f"Clearing 0/{limit} messages", ephemeral=True)
        response = await interaction.original_response()
        dm = await interaction.user.create_dm()
        counter = 0
        async for msg in dm.history(limit=limit):
            try:
                await msg.delete()
                counter += 1
                await response.edit(content=f"Clearing {counter}/{limit} messages")
                await asyncio.sleep(0.1)
            except Forbidden:
                pass
        await response.edit(content=f"Done. Cleared {counter} messages", delete_after=30)

    @bot.command()
    @commands.is_owner()
    @commands.guild_only()
    async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object],
                   spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1

        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    async def send_notify_message(*, msg: str = None, title: str = "Info", critical: bool = False,
                                  extra_first_field_name: str = None, extra_first_field_value: str = None):
        channel = await bot.fetch_channel(1237549044675641425)
        embed = discord.Embed(
            title=title,
            color=discord.Colour.red() if critical else discord.Colour.default(),
            timestamp=datetime.now()
        )
        if extra_first_field_name or extra_first_field_value:
            embed.add_field(name=extra_first_field_name, value=extra_first_field_value, inline=False)
        if msg:
            curr_msg = ""
            for line in msg.split("\n"):
                next_msg = curr_msg + line + "\n"
                if len(next_msg) > 1024:
                    embed.add_field(name="", value=curr_msg, inline=False)
                    curr_msg = line + "\n"
                else:
                    curr_msg = next_msg

        log_msg = title
        if msg:
            log_msg += " " + msg
        if critical:
            log_msg = f"PING {log_msg}"

        if critical:
            await channel.send(content=f"<@{bot.owner_id}>", embed=embed)
            logger.info(log_msg)
        else:
            await channel.send(embed=embed)
            logger.info(log_msg)

    bot.tree.on_error = on_error
    bot.run(token, log_handler=None)
