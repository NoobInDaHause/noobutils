import discord

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
        custom_emoji = emoji.split(":")
        if len(custom_emoji) < 2:
            return None
        custom_emoji = custom_emoji[2].replace(">", "")
        try:
            d = int(custom_emoji)
            return discord.utils.get(context.bot.emojis, id=d)
        except Exception:
            return None
