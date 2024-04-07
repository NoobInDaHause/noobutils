from __future__ import annotations

import contextlib
import datetime as dt
import discord

from redbot.core.bot import app_commands, commands, Red

from emoji import EMOJI_DATA
from rapidfuzz import process
from typing import Collection, List, Optional, Union
from unidecode import unidecode


class NoobCoordinate(dict):
    def __missing__(self, key: str):
        return "{" + key + "}"


class NoobEmojiConverter(app_commands.Transformer):
    url: str
    guild: discord.Guild
    guild_id: int
    animated: bool
    created_at: dt.datetime
    roles: List[discord.Role]
    user: discord.User
    name: str

    @classmethod
    async def convert(
        cls, ctx: commands.Context, argument: str
    ) -> Union[discord.Emoji, str]:
        if argument.strip() in EMOJI_DATA.keys():
            return argument.strip()
        else:
            return await commands.EmojiConverter().convert(ctx, argument.strip())

    @classmethod
    async def transform(
        cls, interaction: discord.Interaction[Red], value: str
    ) -> Union[discord.Emoji, str]:
        ctx = await interaction.client.get_context(interaction)
        return await cls.convert(ctx, value)

    async def delete(self, *, reason: Optional[str] = None) -> None:
        raise NotImplementedError("This is only used for type hinting.")

    async def edit(
        self,
        *,
        name: str = discord.utils.MISSING,
        roles: Collection[discord.abc.Snowflake] = discord.utils.MISSING,
        reason: Optional[str] = None,
    ) -> discord.Emoji:
        raise NotImplementedError("This is only used for type hinting.")


# https://github.com/phenom4n4n/phen-cogs/blob/327fc78c66814ac01f644c6b775dc4d6db6e1e5f/roleutils/converters.py#L36
# original converter from https://github.com/TrustyJAID/Trusty-cogs/blob/master/serverstats/converters.py#L19
class NoobFuzzyRole(app_commands.Transformer):
    """
    This will accept role ID's, mentions, and perform a fuzzy search for
    roles within the guild and return a list of role objects
    matching partial names
    Guidance code on how to do this from:
    https://github.com/Rapptz/discord.py/blob/rewrite/discord/ext/commands/converter.py#L85
    https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/mod.py#L24
    """

    color: discord.Color
    colour: discord.Colour
    members: List[discord.Member]
    mention: str
    id: int
    hoist: bool
    guild: discord.Guild
    position: int
    managed: bool
    mentionable: bool
    name: str
    permissions: discord.Permissions
    icon: discord.Asset
    display_icon: Union[discord.Asset, str]
    created_at: dt.datetime

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> discord.Role:
        with contextlib.suppress(commands.BadArgument):
            return await commands.RoleConverter().convert(ctx, argument)
        result = [
            (r[2], r[1])
            for r in process.extract(
                argument,
                {r: unidecode(r.name) for r in ctx.guild.roles},
                limit=None,
                score_cutoff=75,
            )
        ]
        if not result:
            raise commands.BadArgument(f'Role "{argument}" not found.')

        sorted_result = sorted(result, key=lambda r: r[1], reverse=True)
        return sorted_result[0][0]

    @classmethod
    async def transform(
        cls, interaction: discord.Interaction[Red], value: str
    ) -> discord.Role:
        ctx = await interaction.client.get_context(interaction)
        return await cls.convert(ctx, value)

    def is_premium_subscriber(self) -> bool:
        raise NotImplementedError("This is only used for type hinting.")

    def is_integration(self) -> bool:
        raise NotImplementedError("This is only used for type hinting.")

    def is_assignable(self) -> bool:
        raise NotImplementedError("This is only used for type hinting.")

    def is_bot_managed(self) -> bool:
        raise NotImplementedError("This is only used for type hinting.")

    def is_default(self) -> bool:
        raise NotImplementedError("This is only used for type hinting.")

    async def edit(
        self,
        *,
        name: str = discord.utils.MISSING,
        permissions: discord.Permissions = discord.utils.MISSING,
        colour: Union[discord.Colour, int] = discord.utils.MISSING,
        color: Union[discord.Colour, int] = discord.utils.MISSING,
        hoist: bool = discord.utils.MISSING,
        display_icon: Optional[Union[bytes, str]] = discord.utils.MISSING,
        mentionable: bool = discord.utils.MISSING,
        position: int = discord.utils.MISSING,
        reason: Optional[str] = discord.utils.MISSING,
    ) -> Optional[discord.Role]:
        raise NotImplementedError("This is only used for type hinting.")

    async def delete(self, *, reason: Optional[str] = None) -> None:
        raise NotImplementedError("This is only used for type hinting.")
