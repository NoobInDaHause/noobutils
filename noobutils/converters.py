import discord
import re

from redbot.core.bot import commands

from emoji import EMOJI_DATA
from typing import Union


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


async def noob_emoji_converter(
    context: commands.Context, emoji: str
) -> Union[discord.Emoji, str, None]:
    try:
        EMOJI_DATA[emoji]
        return emoji
    except KeyError:
        custom_emoji = re.sub(r"[0-9]+", "", emoji)
        custom_emoji = custom_emoji.replace("<", "").replace(">", "").replace(":", "")
        return discord.utils.get(context.bot.emojis, name=custom_emoji)
