import discord

from redbot.core.utils import chat_formatting as cf

from typing import Union, List

from .converters import NoobCoordinate
from .exceptions import ButtonColourNotFound, MemberOrGuildNotFound


def is_have_avatar(
    thing: Union[discord.Member, discord.Guild] = None, display_av=False
) -> str:
    if thing is None:
        return ""
    elif isinstance(thing, discord.Member):
        if display_av:
            return thing.display_avatar.url or ""
        else:
            return thing.avatar.url or (thing.display_avatar.url or "")
    elif isinstance(thing, discord.Guild):
        return thing.icon.url or ""
    else:
        raise MemberOrGuildNotFound(f'Member or Guild "{thing}" was not found.')


def access_denied(text_only=False) -> str:
    if text_only:
        return "Access Denied."
    else:
        return "https://cdn.discordapp.com/attachments/1000751975308197918/1110013262835228814/1.mp4"


def get_button_colour(colour: str) -> discord.ButtonStyle:
    """
    blurple, red, green, grey
    """
    if colour.lower() == "blurple":
        return discord.ButtonStyle.blurple
    elif colour.lower() == "red":
        return discord.ButtonStyle.red
    elif colour.lower() == "green":
        return discord.ButtonStyle.green
    elif colour.lower() == "grey":
        return discord.ButtonStyle.grey
    else:
        raise ButtonColourNotFound(f'"{colour}" is not a valid button colour.')


async def pagify_this(
    big_ass_variable_string: str,
    delim: str,
    page_text: str,
    page_char: int = 2000,
    is_embed: bool = True,
    embed_title: str = None,
    embed_colour: discord.Colour = None,
    footer_icon: str = None,
) -> List[Union[discord.Embed, str]]:
    final_page: List[Union[discord.Embed, str]] = []
    if is_embed:
        pages = list(
            cf.pagify(big_ass_variable_string, delims=[delim], page_length=page_char)
        )
    else:
        pages = list(
            cf.pagify(
                big_ass_variable_string, delims=[delim], page_length=(page_char - 50)
            )
        )

    for index, page in enumerate(pages, 1):
        if is_embed:
            embed = discord.Embed(
                title=embed_title, colour=embed_colour, description=page
            ).set_footer(
                text=page_text.format_map(
                    NoobCoordinate(index=index, pages=len(pages))
                ),
                icon_url=footer_icon,
            )
            final_page.append(embed)
        else:
            t = "{page}\n\n{page_text}".format_map(
                NoobCoordinate(
                    page=page, page_text=page_text, index=index, pages=len(pages)
                )
            )
            final_page.append(t)
    return final_page
