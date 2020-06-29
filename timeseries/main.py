"""
MIT License

Copyright (c) 2019 Predä

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import asyncio
import contextlib
import logging
import concurrent
from collections import Counter
from typing import List, Mapping

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS

from redbot.core.bot import Red
from redbot.core import commands, checks, Config
from redbot.core.utils import AsyncIter

from timeseries.stats_task import start_stats_tasks, call_sync_as_async, init_bot_stats

log = logging.getLogger("red.predacogs.TimeSeries")


class TimeSeries(commands.Cog):
    """Get multiple stats of your bot sent to an InfluxDB instance."""

    # This cog is an adaptation of what Draper done first, my personal changes,
    # and other stuff that I've done for a bounty.

    __author__ = ["Draper#6666", "Predä 。#1001"]
    __version__ = "1.0"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=332980470202044161, force_registration=True)
        self.config.register_global(
            url="http://localhost:9999",
            bucket="bucket",
            org="org",
            commands_stats=Counter({}),
            detailed=True,
        )
        self.commands_cache = {"session": Counter(), "persistent": Counter()}

        self._start_task = bot.loop.create_task(self.initialise())
        self._tasks: List[asyncio.Task] = []
        init_bot_stats(self.bot)

        self.client = {"client": None, "bucket": None, "write_api": None}
        self.api_ready = False

    async def initialise(self):
        val = getattr(self.bot, "_stats_task", None)
        recreate = False
        if val is None:
            recreate = True
        elif val:
            if isinstance(val, asyncio.Task):
                recreate = True
                if not val.done():
                    val.cancel()
            else:
                recreate = True
        if recreate:
            self.bot._stats_task = asyncio.create_task(start_stats_tasks(self.bot, self.config))
        await self.wait_until_stats_ready()
        await self.connect_to_influx()
        self.commands_cache["persistent"] = await self.config.commands_stats()
        await self.start_tasks()

    async def wait_until_stats_ready(self):
        """Wait until stats task has done its first loop."""
        await self.bot._stats_ready.wait()

    def cog_unload(self):
        self.bot.loop.create_task(self.update_command_usage())
        if self._start_task:
            self._start_task.cancel()
        for task in self._tasks:
            with contextlib.suppress(Exception):
                task.cancel()

        if self.client["client"]:
            self.client["client"].__del__()
            self.client["write_api"].__del__()

        if getattr(self.bot, "_stats_task", None):
            self.bot._stats_task.cancel()

    async def connect_to_influx(self, token=None):
        if self.api_ready:
            self.client["client"].__del__()
            self.client["write_api"].__del__()
            self.client = {"client": None, "bucket": None, "write_api": None}
            self.api_ready = False

        config = await self.config.all()
        token = (
            token.get("api_key", "")
            if token
            else (await self.bot.get_shared_api_tokens("timeseries")).get("api_key", "")
        )
        client = InfluxDBClient(
            url=config["url"], org=config["org"], token=token, enable_gzip=True,
        )
        if client.health().status == "pass":
            self.client = {
                "client": client,
                "bucket": config["bucket"],
                "write_api": client.write_api(write_options=ASYNCHRONOUS),
            }
            self.api_ready = True
        else:
            client.close()
        return self.api_ready

    @commands.Cog.listener()
    async def on_red_api_tokens_update(self, service_name: str, api_tokens: Mapping[str, str]):
        if service_name != "timeseries":
            return
        await self.connect_to_influx(api_tokens)

    async def update_command_usage(self):
        await self.config.commands_stats.set(self.commands_cache["persistent"])
        self.commands_cache["session"].clear()
        self.commands_cache["persistent"].clear()

    async def write_bot_data(self):
        if not self.api_ready:
            return
        unchunked_guilds = len(
            [
                guild
                async for guild in AsyncIter(self.bot.guilds, steps=25)
                if not guild.chunked and not guild.unavailable and guild.large
            ]
        )
        p = Point("-")
        for k, v in self.bot.stats.bot.__dict__.items():
            if unchunked_guilds >= 8 and k == "Unique Users":
                continue
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

        p = Point("Server Region")
        for k, v in self.bot.stats.guilds_regions.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

        p = Point("Servers")
        for k, v in self.bot.stats.guilds.__dict__.items():
            if unchunked_guilds >= 8 and k == "Members":
                continue
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

        p = Point("Server Features")
        for k, v in self.bot.stats.guild_features.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

        p = Point("Server Verification")
        for k, v in self.bot.stats.guild_verification.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    async def write_audio_data(self):
        if not self.api_ready:
            return
        p = Point("Audio")
        for k, v in self.bot.stats.audio.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    async def write_shard_latencies_data(self):
        if not self.api_ready:
            return
        p = Point("Shard")
        for k, v in self.bot.stats.shards.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    async def write_currency_data(self):
        if not self.api_ready:
            return
        p = Point("-")
        for k, v in self.bot.stats.currency.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    async def write_commands_data(self):
        if not self.api_ready:
            return
        p = Point("Commands")
        for k, v in self.commands_cache["session"].items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

        p = Point("Commands Persistent")
        for k, v in self.commands_cache["persistent"].items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    async def write_adventure_data(self):
        if not self.api_ready:
            return
        if self.bot.get_cog("Adventure") is None:
            return
        p = Point("Adventure")
        for k, v in self.bot.stats.adventure.__dict__.items():
            p.field(k, v)
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        if not self.api_ready:
            return
        if ctx.message.author.bot:
            return
        command = ctx.command.qualified_name
        self.commands_cache["session"][command] += 1
        p = Point("Commands")
        p.field(command, self.commands_cache["session"][command])
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

        self.commands_cache["persistent"][command] += 1
        p = Point("Commands Persistent")
        p.field(command, self.commands_cache["persistent"][command])
        call_sync_as_async(self.client["write_api"].write, bucket=self.client["bucket"], record=p)

    async def start_tasks(self):
        for task in [self.update_task, self.save_commands_stats]:
            self._tasks.append(asyncio.create_task(task(self.bot)))

    async def run_events(self):
        if not self.api_ready:
            return
        await asyncio.gather(
            *[
                self.write_bot_data(),
                self.write_currency_data(),
                self.write_shard_latencies_data(),
                self.write_audio_data(),
                self.write_commands_data(),
                self.write_adventure_data(),
            ],
            return_exceptions=True,
        )

    async def update_task(self, bot):
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                try:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        executor.submit(await self.run_events())
                except asyncio.CancelledError:
                    break
                except Exception as exc:
                    log.exception("update_task", exc_info=exc)
                else:
                    await asyncio.sleep(15)

    async def save_commands_stats(self, bot):
        with contextlib.suppress(asyncio.CancelledError):
            while True:
                await asyncio.sleep(1800)
                await self.config.commands_stats.set(self.commands_cache["persistent"])

    @checks.is_owner()
    @commands.group()
    async def timeseriesset(self, ctx: commands.Context):
        """Settings for InfluxDB API."""

    @timeseriesset.command()
    async def url(self, ctx: commands.Context, *, url: str = "http://localhost:9999"):
        """Set the InfluxDB url. Default is `http://localhost:9999`."""
        await self.config.url.set(url)
        connection = await self.connect_to_influx()
        await ctx.tick() if connection else await ctx.send(
            "Cannot connect to that URL. Please make sure that it is correct or to also set a bucket and organization name."
        )

    @timeseriesset.command()
    async def bucket(self, ctx: commands.Context, *, bucket: str = None):
        """Set the bucket name."""
        await self.config.bucket.set(bucket)
        connection = await self.connect_to_influx()
        await ctx.tick() if connection else await ctx.send(
            "Cannot connect with that bucket name. Please make sure that it is correct or to also set an URL and an organization name."
        )

    @timeseriesset.command()
    async def org(self, ctx: commands.Context, *, org: str = None):
        """Set the organization name."""
        await self.config.org.set(org)
        connection = await self.connect_to_influx()
        await ctx.tick() if connection else await ctx.send(
            "Cannot connect with that organization name. Please make sure that it is correct or to also set an URL and a bucket name."
        )

    @timeseriesset.command()
    async def token(self, ctx: commands.Context):
        """Instructions on how to set the token."""
        msg = f"Use `{ctx.prefix}set api timeseries api_key your_api_key_here`."
        await ctx.send(msg)

    @timeseriesset.command()
    async def detailed(self, ctx: commands.Context):
        """Toggles whether to send more detailed data (More resource intensive)."""
        state = await self.config.detailed()
        await self.config.detailed.set(not state)
        new_state = "Enabled" if not state else "Disabled"
        await ctx.send(f"Detailed stats submission: {new_state}")
