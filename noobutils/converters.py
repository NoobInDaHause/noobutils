from __future__ import annotations

import discord

from redbot.core import commands

from datetime import datetime
from emoji import EMOJI_DATA
from rapidfuzz import process
from typing import List, Union
from unidecode import unidecode

from .exceptions import FuzzyRoleConversionFailure


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(commands.EmojiConverter):
    def __init__(self, emoji: Union[discord.Emoji, str]):
        super().__init__()
        self._emoji = emoji

    @classmethod
    async def convert(
        cls, ctx: commands.Context, argument: str
    ) -> Union[discord.Emoji, str]:
        if argument.strip() in EMOJI_DATA.keys():
            return cls(emoji=argument.strip())
        else:
            e = await super().convert(ctx, argument.strip())
            return cls(emoji=e)

    @property
    def id(self) -> int:
        return self._emoji.id if isinstance(self._emoji, discord.Emoji) else None

    @property
    def guild(self) -> discord.Guild:
        return self._emoji.guild if isinstance(self._emoji, discord.Emoji) else None

    @property
    def url(self) -> str:
        return self._emoji.url if isinstance(self._emoji, discord.Emoji) else None

    @property
    def animated(self) -> bool:
        return self._emoji.animated if isinstance(self._emoji, discord.Emoji) else False

    @property
    def name(self) -> str:
        return self._emoji.name if isinstance(self._emoji, discord.Emoji) else self._emoji.replace(":", "")

    @property
    def created_at(self) -> datetime:
        return self._emoji.created_at if isinstance(self._emoji, discord.Emoji) else None


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

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            basic_role = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass
        else:
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
            raise FuzzyRoleConversionFailure(
                f'Role "{argument}" not found.'
            )

        sorted_result = sorted(result, key=lambda r: r[1], reverse=True)
        return cls(role=sorted_result[0][0])

    @property
    def id(self) -> int:
        return self._role.id

    @property
    def color(self) -> discord.Color:
        return self._role.color

    @property
    def colour(self) -> discord.Colour:
        return self._role.colour

    @property
    def members(self) -> List[discord.Member]:
        return self._role.members

    @property
    def mentionable(self) -> bool:
        return self._role.mentionable

    @property
    def name(self) -> str:
        return self._role.name

    @property
    def created_at(self) -> datetime:
        return self._role.created_at

    @property
    def mention(self) -> str:
        return self._role.mention

    @property
    def guild(self) -> discord.Guild:
        return self._role.guild

    @property
    def permissions(self) -> discord.Permissions:
        return self._role.permissions

    @property
    def position(self) -> int:
        return self._role.position
