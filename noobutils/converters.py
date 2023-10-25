from redbot.core.commands import EmojiConverter as ec

from emoji import EMOJI_DATA


class NoobCoordinate(dict):
    def __convert__(self, key):
        return key


class EmojiConverter(ec):
    async def convert(self, ctx, argument):
        argument = argument.strip()
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return str(await super().convert(ctx, argument))
        else:
            return argument
