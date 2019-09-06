import asyncio
import contextlib
from collections import Counter
from copy import copy
from datetime import datetime

import discord
import lavalink

from redbot.core import Config, bank, commands
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.chat_formatting import bold, humanize_timedelta

# from redbot.cogs.audio.dataclasses import Query

_ = Translator("MartTools", __file__)


@cog_i18n(_)
class MartTools(commands.Cog):
    """Multiple tools that are originally used on Martine the BOT."""

    __author__ = "Predä"
    __version__ = "1.4.0"

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()
        self.sticky_counter = Counter()
        self.config = Config.get_conf(self, 64481875498, force_registration=True)
        global_defauls = dict(
            command_error=0,
            msg_sent=0,
            dms_received=0,
            messages_read=0,
            guild_join=0,
            guild_remove=0,
            sessions_resumed=0,
            processed_commands=0,
            new_members=0,
            members_left=0,
            messages_deleted=0,
            messages_edited=0,
            reactions_added=0,
            reactions_removed=0,
            roles_added=0,
            roles_removed=0,
            roles_updated=0,
            members_banned=0,
            members_unbanned=0,
            emojis_removed=0,
            emojis_added=0,
            emojis_updated=0,
            users_joined_bot_music_room=0,
        )
        self.config.register_global(**global_defauls)
        self._task = self.bot.loop.create_task(self._save_counters_to_config())
        lavalink.register_event_listener(self.event_handler)  # To delete at next audio update.

    def cog_unload(self):
        lavalink.unregister_event_listener(self.event_handler)  # To delete at next audio update.
        self.bot.loop.create_task(self._clean_up())

    async def event_handler(self, player, event_type, extra):  # To delete at next audio update.
        # Thanks Draper#6666
        if event_type == lavalink.LavalinkEvents.TRACK_START:
            self.update_counters("tracks_played")

    def update_counters(self, key: str):
        self.counter[key] += 1
        self.sticky_counter[key] += 1

    def get_bot_uptime(self):
        delta = datetime.utcnow() - (
            self.bot.uptime if hasattr(self.bot, "uptime") else self.bot._uptime
        )
        uptime = humanize_timedelta(timedelta=delta)
        return uptime

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error, unhandled_by_cog=False):
        if not unhandled_by_cog:
            if hasattr(ctx.command, "on_error"):
                return

            if ctx.cog:
                if commands.Cog._get_overridden_method(ctx.cog.cog_command_error) is not None:
                    return
        if isinstance(
            error,
            (
                commands.MissingRequiredArgument,
                commands.ConversionFailure,
                commands.UserInputError,
                commands.DisabledCommand,
                commands.CommandNotFound,
                commands.BotMissingPermissions,
                commands.UserFeedbackCheckFailure,
                commands.CheckFailure,
                commands.NoPrivateMessage,
                commands.CommandOnCooldown,
                getattr(commands, "ArgParserFailure", commands.UserInputError),
            ),
        ):
            return
        self.update_counters("command_error")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            self.update_counters("msg_sent")
        if message.guild is None:
            self.update_counters("dms_received")
        self.update_counters("messages_read")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        self.update_counters("guild_join")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        self.update_counters("guild_remove")

    @commands.Cog.listener()
    async def on_resumed(self):
        self.update_counters("sessions_resumed")

    @commands.Cog.listener()
    async def on_command(self, command):
        self.update_counters("processed_commands")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.update_counters("new_members")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.update_counters("members_left")

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.update_counters("messages_deleted")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.update_counters("messages_edited")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        self.update_counters("reactions_added")

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        self.update_counters("reactions_removed")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        self.update_counters("roles_added")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        self.update_counters("roles_removed")

    @commands.Cog.listener()
    async def on_guild_role_update(self, role):
        self.update_counters("roles_updated")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        self.update_counters("members_banned")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        self.update_counters("members_unbanned")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        if len(before) > len(after):
            self.update_counters("emojis_removed")
        elif len(before) < len(after):
            self.update_counters("emojis_added")
        else:
            self.update_counters("emojis_updated")

    @commands.Cog.listener()
    async def on_voice_state_update(
        self, member, before: discord.VoiceState, after: discord.VoiceState
    ):
        if not after.channel:
            return
        guild = after.channel.guild
        bot_in_room = guild.me in after.channel.members
        if bot_in_room:
            self.update_counters("users_joined_bot_music_room")

    # @commands.Cog.listener()
    # async def on_red_audio_track_start(self, guild, track, requester):
    #     self.update_counters("tracks_played")
    #     query = Query.process_input(track)
    #
    #     if track.is_stream:
    #         self.update_counters("streams_played")
    #         if query.is_youtube:
    #             self.update_counters("yt_streams_played")
    #         elif query.is_mixer:
    #             self.update_counters("mixer_streams_played")
    #         elif query.is_twitch:
    #             self.update_counters("ttv_streams_played")
    #         elif query.is_other:
    #             self.update_counters("other_streams_played")
    #
    #     if query.is_youtube:
    #         self.update_counters("youtube_tracks")
    #     elif query.is_soundcloud:
    #         self.update_counters("soundcloud_tracks")
    #     elif query.is_bandcamp:
    #         self.update_counters("bandcamp_tracks")
    #     elif query.is_vimeo:
    #         self.update_counters("vimeo_tracks")
    #     elif query.is_mixer:
    #         self.update_counters("mixer_tracks")
    #     elif query.is_twitch:
    #         self.update_counters("twitch_tracks")
    #     elif query.is_other:
    #         self.update_counters("other_tracks")

    async def _save_counters_to_config(self):
        await self.bot.wait_until_ready()
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                _date = datetime.utcnow().timestamp()
                users_data = copy(self.sticky_counter)
                self.sticky_counter = Counter()
                async with self.config.all() as new_data:
                    for key, value in users_data.items():
                        new_data[key] += value
                    if "start_date" not in new_data:
                        new_data["start_date"] = _date
                await asyncio.sleep(60)

    async def _clean_up(self):
        if self._task:
            self._task.cancel()
        async with self.config.all() as new_data:
            for key, value in self.sticky_counter.items():
                new_data[key] += value

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def bankstats(self, ctx):
        """Show stats of the bank."""
        icon = self.bot.user.avatar_url_as(static_format="png")
        user_bal = await bank.get_balance(ctx.author)
        credits_name = await bank.get_currency_name(ctx.guild)
        pos = await bank.get_leaderboard_position(ctx.author)
        bank_name = await bank.get_bank_name(ctx.guild)
        if await bank.is_global():
            all_accounts = len(await bank._conf.all_users())
            accounts = await bank._conf.all_users()
        else:
            all_accounts = len(await bank._conf.all_members(ctx.guild))
            accounts = await bank._conf.all_members(ctx.guild)
        member_account = await bank.get_account(ctx.author)
        created_at = str(member_account.created_at)
        no = "1970-01-01 00:00:00"
        overall = 0
        for key, value in accounts.items():
            overall += value["balance"]

        em = discord.Embed(color=await ctx.embed_colour())
        em.set_author(name=_("{} stats:").format(bank_name), icon_url=icon)
        em.add_field(
            name=_("{} stats:").format("Global" if await bank.is_global() else "Bank"),
            value=_(
                "Total accounts: **{all_accounts}**\nTotal amount: **{overall:,} {credits_name}**"
            ).format(all_accounts=all_accounts, overall=overall, credits_name=credits_name),
        )
        if pos is not None:
            percent = round((int(user_bal) / overall * 100), 3)
            em.add_field(
                name=_("Your stats:"),
                value=_(
                    "You have **{bal:,} {currency}**.\n"
                    "It's **{percent}%** of the {g}amount in the bank.\n"
                    "You are **{pos:,}/{all_accounts:,}** in the {g}leaderboard."
                ).format(
                    bal=user_bal,
                    currency=credits_name,
                    percent=percent,
                    g="global " if await bank.is_global() else "",
                    pos=pos,
                    all_accounts=all_accounts,
                ),
                inline=False,
            )
        if created_at != no:
            em.set_footer(text=_("Bank account created on: ") + str(created_at))
        await ctx.send(embed=em)

    @commands.command(aliases=["usagec"])
    async def usagecount(self, ctx):
        """
            Show the usage count of the bot.
            Commands processed, messages received, and music on servers.
        """
        uptime = str(self.get_bot_uptime())
        commands_count = "`{:,}`".format(self.counter["processed_commands"])
        errors_count = "`{:,}`".format(self.counter["command_error"])
        messages_read = "`{:,}`".format(self.counter["messages_read"])
        messages_sent = "`{:,}`".format(self.counter["msg_sent"])
        try:
            total_num = "`{:,}/{:,}`".format(
                len(lavalink.active_players()), len(lavalink.all_players())
            )
        except AttributeError:
            total_num = "`{:,}/{:,}`".format(
                len([p for p in lavalink.players if p.current is not None]),
                len([p for p in lavalink.players]),
            )
        tracks_played = "`{:,}`".format(self.counter["tracks_played"])
        guild_join = "`{:,}`".format(self.counter["guild_join"])
        guild_leave = "`{:,}`".format(self.counter["guild_remove"])
        avatar = self.bot.user.avatar_url_as(static_format="png")
        msg = (
            bold(_("Commands processed: "))
            + _("{} commands.\n").format(commands_count)
            + bold(_("Commands errors: "))
            + _("{} errors.\n").format(errors_count)
            + bold(_("Messages received: "))
            + _("{} messages.\n").format(messages_read)
            + bold(_("Messages sent: "))
            + _("{} messages.\n").format(messages_sent)
            + bold(_("Playing music on: "))
            + _("{} servers.\n").format(total_num)
            + bold(_("Tracks played: "))
            + _("{} tracks.\n\n").format(tracks_played)
            + bold(_("Servers joined: "))
            + _("{} servers.\n").format(guild_join)
            + bold(_("Servers left: "))
            + _("{} servers.").format(guild_leave)
        )
        try:
            em = discord.Embed(color=await ctx.embed_colour())
            em.add_field(
                name=_("Usage count of {} since last restart:").format(ctx.bot.user.name),
                value=msg,
            )
            em.set_thumbnail(url=avatar)
            em.set_footer(text=_("Since {}").format(uptime))
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send(
                _("Usage count of {} since last restart:\n").format(ctx.bot.user.name)
                + msg
                + _("\n\nSince {}").format(uptime)
            )

    @commands.command(aliases=["prefixes"])
    async def prefix(self, ctx):
        """Show all prefixes of the bot"""
        default_prefixes = await ctx.bot.db.prefix()
        try:
            guild_prefixes = await ctx.bot.db.guild(ctx.guild).prefix()
        except AttributeError:
            guild_prefixes = False
        bot_name = ctx.bot.user.name
        avatar = self.bot.user.avatar_url_as(static_format="png")

        if not guild_prefixes:
            to_send = [f"`\u200b{p}\u200b`" for p in default_prefixes]
            plural = _("es") if len(default_prefixes) >= 2 else ""
            try:
                em = discord.Embed(color=await ctx.embed_colour())
                em.add_field(
                    name=_("Prefix{es} of {name}:").format(es=plural, name=bot_name),
                    value=" ".join(to_send),
                )
                em.set_thumbnail(url=avatar)
                await ctx.send(embed=em)
            except discord.Forbidden:
                await ctx.send(
                    bold(_("Prefix{es} of {name}:\n")).format(es=plural, name=bot_name)
                    + " ".join(to_send)
                )
        else:
            to_send = [f"`\u200b{p}\u200b`" for p in guild_prefixes]
            plural = _("es") if len(guild_prefixes) >= 2 else ""
            try:
                em = discord.Embed(color=await ctx.embed_colour())
                em.add_field(
                    name=_("Server prefix{es} of {name}:").format(es=plural, name=bot_name),
                    value=" ".join(to_send),
                )
                em.set_thumbnail(url=avatar)
                await ctx.send(embed=em)
            except discord.Forbidden:
                await ctx.send(
                    bold(_("Server prefix{es} of {name}:\n")).format(es=plural, name=bot_name)
                    + " ".join(to_send)
                )

    @commands.command(aliases=["serverc", "serversc"])
    async def servercount(self, ctx):
        """Send servers stats of the bot."""
        shards = self.bot.shard_count
        servers = len(self.bot.guilds)
        channels = sum(len(s.channels) for s in self.bot.guilds)
        total_users = sum(len(s.members) for s in self.bot.guilds)
        unique = len(self.bot.users)

        msg = _(
            "{name} is running on `{shards:,}` shard{s}.\n"
            "Serving `{servs:,}` servers (`{channels:,}` channels).\n"
            "For a total of `{users:,}` users (`{unique:,}` unique)."
        ).format(
            name=ctx.bot.user.name,
            shards=shards,
            s="s" if shards >= 2 else "",
            servs=servers,
            channels=channels,
            users=total_users,
            unique=unique,
        )
        try:
            em = discord.Embed(color=await ctx.embed_colour(), description=msg)
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send(msg)

    @commands.command(aliases=["servreg"])
    async def serversregions(self, ctx):
        """Show total of regions where the bot is."""
        regions = {
            "vip-us-east": ":flag_us:" + _(" __VIP__ US East"),
            "vip-us-west": ":flag_us:" + _(" __VIP__ US West"),
            "vip-amsterdam": ":flag_nl:" + _(" __VIP__ Amsterdam"),
            "eu-west": ":flag_eu:" + _(" EU West"),
            "eu-central": ":flag_eu:" + _(" EU Central"),
            "london": ":flag_gb:" + _(" London"),
            "frankfurt": ":flag_de:" + _(" Frankfurt"),
            "amsterdam": ":flag_nl:" + _(" Amsterdam"),
            "us-west": ":flag_us:" + _(" US West"),
            "us-east": ":flag_us:" + _(" US East"),
            "us-south": ":flag_us:" + _(" US South"),
            "us-central": ":flag_us:" + _(" US Central"),
            "singapore": ":flag_sg:" + _(" Singapore"),
            "sydney": ":flag_au:" + _(" Sydney"),
            "brazil": ":flag_br:" + _(" Brazil"),
            "hongkong": ":flag_hk:" + _(" Hong Kong"),
            "russia": ":flag_ru:" + _(" Russia"),
            "japan": ":flag_jp:" + _(" Japan"),
            "southafrica": ":flag_za:" + _(" South Africa"),
            "india": ":flag_in:" + _(" India"),
        }
        region = {}
        for guild in self.bot.guilds:
            if str(guild.region):
                if str(guild.region) not in region:
                    region[str(guild.region)] = 0
                region[str(guild.region)] += 1
        divided = []
        for k, v in region.items():
            divided.append([k, v])
        divided = sorted(divided, key=lambda x: x[1], reverse=True)
        new = {}
        for entry in divided:
            new[entry[0]] = entry[1]
        msg = ""
        for k, v in new.items():
            msg += regions[str(k)] + f": `{v}`\n"
        guilds = len(self.bot.guilds)

        try:
            em = discord.Embed(
                color=await ctx.embed_colour(), title=_("Servers regions stats:"), description=msg
            )
            em.set_footer(text=_("For a total of {} servers").format(guilds))
            await ctx.send(embed=em)
        except discord.Forbidden:
            await ctx.send(
                bold(_("Servers regions stats:\n\n"))
                + msg
                + bold(_("\nFor a total of {} servers").format(guilds))
            )
