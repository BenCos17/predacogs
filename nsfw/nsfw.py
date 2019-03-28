import discord

from redbot.core import checks, commands

from .core import Functions
from . import subs


class Nsfw(Functions, commands.Cog):
    """Send random NSFW images from random subreddits"""

    __author__ = ["Predä", "aikaterna"]
    __version__ = "1.1"

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(name="4k", aliases=["4K"])
    async def four_k(self, ctx):
        """Show some 4k images from random subreddits."""

        await self._send_msg(ctx, "4k", sub=subs.FOUR_K, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def ahegao(self, ctx):
        """Show some ahegao images from random subreddits."""

        await self._send_msg(ctx, "ahegao", sub=subs.AHEGAO, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["butt"])
    async def ass(self, ctx):
        """Show some ass images from random subreddits."""

        await self._send_msg(ctx, "ass", sub=subs.ASS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def anal(self, ctx):
        """Show some anal images/gifs from random subreddits."""

        await self._send_msg(ctx, "anal", sub=subs.ANAL, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def bdsm(self, ctx):
        """Show some bdsm from random subreddits."""

        await self._send_msg(ctx, "bdsm", sub=subs.BDSM, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["blackdick", "bcock", "bdick", "blackcocks", "blackdicks"])
    async def blackcock(self, ctx):
        """Show some blackcock images from random subreddits."""

        await self._send_msg(ctx, "black cock", sub=subs.BLACKCOCK, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["blowjobs", "blowj", "bjob"])
    async def blowjob(self, ctx):
        """Show some blowjob images/gifs from random subreddits."""

        await self._send_msg(ctx, "blowjob", sub=subs.BLOWJOB, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["boob", "tits", "titties"])
    async def boobs(self, ctx):
        """Show some boobs images from random subreddits."""

        await self._send_msg(ctx, "boobs", sub=subs.BOOBS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["boless"])
    async def bottomless(self, ctx):
        """Show some bottomless images from random subreddits."""

        await self._send_msg(ctx, "bottomless", sub=subs.BOTTOMLESS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["cunni"])
    async def cunnilingus(self, ctx):
        """Show some cunnilingus images from random subreddits."""

        await self._send_msg(ctx, "cunnilingus", sub=subs.CUNNI, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["cum", "cumshots"])
    async def cumshot(self, ctx):
        """Show some cumshot images/gifs from random subreddits."""

        await self._send_msg(ctx, "cumshot", sub=subs.CUMSHOTS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["deept"])
    async def deepthroat(self, ctx):
        """Show some deepthroat images from random subreddits."""

        await self._send_msg(ctx, "deepthroat", sub=subs.DEEPTHROAT, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def dick(self, ctx):
        """Show some dicks images from random subreddits."""

        await self._send_msg(ctx, "dick", sub=subs.DICK, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["doublep", "dpenetration", "doublepene"])
    async def doublepenetration(self, ctx):
        """Show some double penetration images/gifs from random subreddits."""

        await self._send_msg(ctx, "double penetration", sub=subs.DOUBLE_P, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["nudeman"])
    async def gay(self, ctx):
        """Show some gay porn from random subreddits."""

        await self._send_msg(ctx, "gay porn", sub=subs.GAY_P, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["groups"])
    async def group(self, ctx):
        """Show some groups nudes from random subreddits."""

        await self._send_msg(ctx, "groups nudes", sub=subs.GROUPS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["hentaigif"])
    async def hentai(self, ctx):
        """Show some hentai images/gifs from Nekobot API."""

        await self._make_embed_others(ctx, "hentai", api_category=["hentai_anal", "hentai"])

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def lesbian(self, ctx):
        """Show some lesbian gifs or images from random subreddits."""

        await self._send_msg(ctx, "lesbian", sub=subs.LESBIANS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["milfs"])
    async def milf(self, ctx):
        """Show some milf images from random subreddits."""

        await self._send_msg(ctx, "milf", sub=subs.MILF, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["suck"])
    async def oral(self, ctx):
        """Show some oral gifs or images from random subreddits."""

        await self._send_msg(ctx, "oral", sub=subs.ORAL, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["pgif"])
    async def porngif(self, ctx):
        """Show some porn gifs from Nekobot API."""

        await self._make_embed_others(ctx, "porn gif", api_category=["pgif"])

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def public(self, ctx):
        """Show some public nude images from random subreddits."""

        await self._send_msg(ctx, "public nude", sub=subs.PUBLIC, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def pussy(self, ctx):
        """Show some pussy nude images from random subreddits."""

        await self._send_msg(ctx, "pussy", sub=subs.PUSSY, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command()
    async def realgirls(self, ctx):
        """Show some real girls images from random subreddits."""

        await self._send_msg(ctx, "real nudes", sub=subs.REAL_GIRLS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["redheads", "ginger", "gingers"])
    async def redhead(self, ctx):
        """Show some red heads images from random subreddits."""

        await self._send_msg(ctx, "red head", sub=subs.REDHEADS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["r34"])
    async def rule34(self, ctx):
        """Show some rule34 images from random subreddits."""

        await self._send_msg(ctx, "rule34", sub=subs.RULE_34, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["thighs"])
    async def thigh(self, ctx):
        """Show some thighs images from random subreddits."""

        await self._send_msg(ctx, "thigh", sub=subs.THIGHS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["traps", "trans", "girldick", "girldicks", "shemale", "shemales"])
    async def trap(self, ctx):
        """Show some traps from random subreddits."""

        await self._send_msg(ctx, "trap", sub=subs.TRAPS, subr=None)

    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 0.5, commands.BucketType.user)
    @commands.command(aliases=["gonewild", "gwild"])
    async def wild(self, ctx):
        """Show some gonewild images from random subreddits."""

        await self._send_msg(ctx, "gonewild", sub=subs.WILD, subr=None)
