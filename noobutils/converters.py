from __future__ import annotations

import contextlib
import datetime as dt
import discord

from redbot.core import commands

from emoji import EMOJI_DATA
from rapidfuzz import process
from typing import Collection, List, Optional, Union
from unidecode import unidecode


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(commands.EmojiConverter):
    url: str
    guild: discord.Guild
    guild_id: int
    animated: bool
    created_at: dt.datetime
    roles: List[discord.Role]
    user: discord.User
    name: str

    async def convert(
        self, ctx: commands.Context, argument: str
    ) -> Union[discord.Emoji, str]:
        if argument.strip() in EMOJI_DATA.keys():
            return argument.strip()
        else:
            return await super().convert(ctx, argument.strip())

    async def delete(self, *, reason: Optional[str] = None) -> None:
        pass

    async def edit(
        self,
        *,
        name: str = discord.utils.MISSING,
        roles: Collection[discord.abc.Snowflake] = discord.utils.MISSING,
        reason: Optional[str] = None,
    ) -> discord.Emoji:
        pass


# https://github.com/phenom4n4n/phen-cogs/blob/327fc78c66814ac01f644c6b775dc4d6db6e1e5f/roleutils/converters.py#L36
# original converter from https://github.com/TrustyJAID/Trusty-cogs/blob/master/serverstats/converters.py#L19
class NoobFuzzyRole(commands.RoleConverter):
    """
    This will accept role ID's, mentions, and perform a fuzzy search for
    roles within the guild and return a list of role objects
    matching partial names
    Guidance code on how to do this from:
    https://github.com/Rapptz/discord.py/blob/rewrite/discord/ext/commands/converter.py#L85
    https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/mod.py#L24
    """

    def __init__(self, role: discord.Role):
        super().__init__()
        self._role = role
        self.color: discord.Color = role.color
        self.colour: discord.Colour = role.colour
        self.members: List[discord.Member] = role.members
        self.mention: str = role.mention
        self.id: int = role.id
        self.hoist: bool = role.hoist
        self.guild: discord.Guild = role.guild
        self.position: int = role.position
        self.managed: bool = role.managed
        self.mentionable: bool = role.mentionable
        self.name: str = role.name
        self.permissions: discord.Permissions = role.permissions
        self.icon: discord.Asset = role.icon
        self.display_icon: Union[discord.Asset, str] = role.display_icon
        self.created_at: dt.datetime = role.created_at

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> discord.Role:
        with contextlib.suppress(commands.BadArgument):
            basic_role = await super().convert(None, ctx, argument)
            return cls(role=basic_role)
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
        return cls(role=sorted_result[0][0])

    def is_premium_subscriber(self) -> bool:
        return self._role.is_premium_subscriber()

    def is_integration(self) -> bool:
        return self._role.is_integration()

    def is_assignable(self) -> bool:
        return self._role.is_assignable()

    def is_bot_managed(self) -> bool:
        return self._role.is_bot_managed()

    def is_default(self) -> bool:
        return self._role.is_default()

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
        return await self._role.edit(
            name=name,
            permissions=permissions,
            colour=colour,
            color=color,
            hoist=hoist,
            display_icon=display_icon,
            mentionable=mentionable,
            position=position,
            reason=reason,
        )

    async def delete(self, *, reason: Optional[str] = None) -> None:
        return await self._role.delete(reason=reason)
