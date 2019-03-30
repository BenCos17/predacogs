import discord

from redbot.core import checks, commands, Config

from typing import Union

import aiohttp

DBL_BASE_URL = "https://discordbots.org/api/bots/"


class DblTools(commands.Cog):
    """Tools to get bots information from discordbots.org."""

    __author__ = "Predä"
    __version__ = "0.1"

    def __init__(self, bot):
        defaut = {"dbl_key": None}
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.config = Config.get_conf(self, 3329804706503720961, force_registration=True)
        self.config.register_global(**defaut)

    async def _get_info(self, ctx, bot=None, info=None, stats=None):
        """Get info from discordbots.org."""
        key = await self.config.dbl_key()
        headers = {"Authorization": key}
        async with self.session.get(DBL_BASE_URL + f"{bot}", headers=headers) as r:
            info = await r.json(content_type=None)
        async with self.session.get(DBL_BASE_URL + f"{bot}" + "/stats", headers=headers) as r:
            stats = await r.json(content_type=None)
        return info, stats

    @checks.is_owner()
    @commands.group()
    async def dblset(self, ctx):
        """Settings for DblTools cog."""
        pass

    @checks.is_owner()
    @dblset.command()
    async def key(self, ctx, key):
        """
        Set your DBL key with this command only in DM.
        Note : You need to have a bot published
        on DBL to use API and have a key.
        """
        if not isinstance(ctx.channel, discord.DMChannel):
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass

            return await ctx.send("You need to use this command in DM.")

        await self.config.dbl_key.set(key)
        await ctx.send("API key set.")

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def dblinfo(self, ctx, bot: Union[int, discord.User] = None):
        """
        Show information of a choosen bot on discordbots.org.

        `[bot]` : Can be a mention or ID of a bot.
        """
        if await self.config.dbl_key() is None:
            return await ctx.send("Owner of this bot need to set an API key first !")
        if bot is None:
            return await ctx.send_help()
        if type(bot) == int:
            try:
                bot = await self.bot.get_user_info(bot)
            except discord.errors.NotFound:
                return await ctx.send(f"{str(bot)} is not a Discord user.")

        try:
            async with ctx.typing():
                info, stats = await self._get_info(ctx, bot=bot.id, info=None, stats=None)
                try:
                    desc = "**Description :**\n```{}```\n".format(str(info["shortdesc"]))
                except:
                    desc = ""
                try:
                    tag = "**Tags :**\n```{}```\n".format(", ".join(info["tags"]))
                except:
                    tag = ""
                try:
                    pfix = "**Prefix :** {}\n".format(str(info["prefix"]))
                except:
                    pfix = ""
                try:
                    libr = "**Library :** {}\n".format(str(info["lib"]))
                except:
                    libr = ""
                try:
                    serv = "**Server count :** {:,}\n".format(stats["server_count"])
                except:
                    serv = ""
                try:
                    shard = "**Shard count :** {:,}\n".format(stats["shard_count"])
                except:
                    shard = ""
                try:
                    mvotes = "{:,}".format(info["monthlyPoints"])
                except:
                    mvotes = "0"
                try:
                    tvotes = "{:,}".format(info["points"])
                except:
                    tvotes = "0"
                format_kwargs = {
                    "description": desc,
                    "tags": tag,  # <:dblCertified:392249976639455232>
                    "if_cert": "**Certified !** \N{WHITE HEAVY CHECK MARK}\n" if info["certifiedBot"] == True else "",
                    "prefix": pfix,
                    "lib": libr,
                    "servs": serv,
                    "shards": shard,
                    "m_votes": "**Monthly votes :** {}\n".format(mvotes),
                    "t_votes": "**Total votes :** {}\n\n".format(tvotes),
                    "dbl_page": "[DBL Page]({})".format(f"https://discordbots.org/bot/{bot.id}"),
                    "if_inv": " • [Invitation link]({})".format(str(info["invite"])) if info["invite"] else "",
                    "if_supp": " • [Support](https://discord.gg/{})".format(str(info["support"])) if info["support"] else "",
                    "if_gh": " • [GitHub]({})".format(str(info["github"])) if info["github"] else "",
                    "if_wsite": " • [Website]({})".format(str(info["website"])) if info["website"] else "",
                }
                description = (
                    "{description}"
                    "{tags}"
                    "{if_cert}"
                    "{prefix}"
                    "{lib}"
                    "{servs}{shards}"
                    "{m_votes}"
                    "{t_votes}"
                    "{dbl_page}{if_inv}{if_supp}{if_gh}{if_wsite}"
                ).format(**format_kwargs)
                em = discord.Embed(color=(await ctx.embed_colour()), description=description)
                em.set_author(
                    name="DBL Stats of {} :".format(str(info["username"])),
                    icon_url="https://cdn.discordapp.com/emojis/393548388664082444.gif",
                )
                em.set_thumbnail(url=bot.avatar_url_as(static_format="png"))
                return await ctx.send(embed=em)
        except:
            return await ctx.send(
                "It doesn't seem to be a valid ID. Try again or check if the ID is right."
            )

    def __unload(self):
        self.bot.loop.create_task(self.session.close())
