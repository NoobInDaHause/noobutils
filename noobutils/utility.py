import discord

from redbot.core.utils import chat_formatting as cf

from typing import Union, List

from .converters import NoobCoordinate
from .exceptions import ButtonColourNotFound, MemberOrGuildNotFound


def is_have_avatar(
    thing: Union[discord.Member, discord.Guild] = None, display_av=False
) -> str:
    if isinstance(thing, discord.Member):
        return (
            thing.display_avatar.url
            if display_av
            else (thing.avatar.url or thing.display_avatar.url or "")
        )
    elif isinstance(thing, discord.Guild):
        return thing.icon.url or ""
    elif thing is None:
        return ""
    else:
        raise MemberOrGuildNotFound(f'Member or Guild "{thing}" was not found.')


def access_denied(text_only=False) -> str:
    return (
        "Access Denied."
        if text_only
        else "[Access Denied.](https://cdn.discordapp.com/attachments/1000751975308197918/1110013262835228814/1.mp4)"
    )


def get_button_colour(colour: str) -> discord.ButtonStyle:
    valid_colours = {
        "blurple": discord.ButtonStyle.blurple,
        "red": discord.ButtonStyle.red,
        "green": discord.ButtonStyle.green,
        "grey": discord.ButtonStyle.grey,
    }
    colour_lower = colour.lower()
    if colour_lower in valid_colours:
        return valid_colours[colour_lower]
    raise ButtonColourNotFound(f'"{colour}" is not a valid button colour.')


async def pagify_this(
    big_ass_variable_string: str,
    delim: str,
    page_text: str = "Page ({index}/{pages})",
    page_char: int = 2000,
    is_embed: bool = True,
    embed_title: str = None,
    embed_colour: discord.Colour = None,
    footer_icon: str = None,
) -> List[Union[discord.Embed, str]]:
    final_page = []
    page_length = page_char if is_embed else (page_char - 50)
    pages = list(
        cf.pagify(big_ass_variable_string, delims=[delim], page_length=page_length)
    )

    for index, page in enumerate(pages, 1):
        formatted_page_text = page_text.format_map(
            NoobCoordinate(index=index, pages=len(pages))
        )
        if is_embed:
            embed = discord.Embed(
                title=embed_title, colour=embed_colour, description=page
            )
            embed.set_footer(text=formatted_page_text, icon_url=footer_icon)
            final_page.append(embed)
        else:
            text = f"{page}\n\n{formatted_page_text}"
            final_page.append(text)

    return final_page
