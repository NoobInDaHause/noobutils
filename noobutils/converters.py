from redbot.core.commands import EmojiConverter as ec

from emoji import EMOJI_DATA

from .exceptions import UnknownEmoji


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class NoobEmojiConverter(ec):
    async def convert(self, ctx, argument):
        argument = argument.strip()
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return str(await super().convert(ctx, argument))
        else:
            raise UnknownEmoji(f'Emoji "{argument}" not found.')
