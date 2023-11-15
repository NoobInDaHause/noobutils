import discord

from redbot.core.utils import chat_formatting as cf

from datetime import datetime
from typing import Union, List

from .converters import NoobCoordinate
from .exceptions import ButtonColourNotFound, MemberOrGuildNotFound


def is_have_avatar(
    thing: Union[discord.Member, discord.Guild] = None, display_av=False
) -> str:
    if thing is None:
        return ""
    elif isinstance(thing, discord.Member):
        return (
            thing.display_avatar.url
            if display_av
            else thing.avatar.url
            if thing.avatar
            else thing.display_avatar.url
            if thing.display_avatar
            else ""
        )
    elif isinstance(thing, discord.Guild):
        return thing.icon.url if thing.icon else ""
    else:
        raise MemberOrGuildNotFound(f'Member or Guild "{thing}" was not found.')


def access_denied(text_only=False) -> str:
    return (
        "Access Denied."
        if text_only
        else (
            "[Access Denied.](https://cdn.discordapp.com/attachments/1000751975308197918/1110013262835228814/1.mp4)"
        )
    )


def get_button_colour(colour: str) -> discord.ButtonStyle:
    valid_colours = {
        "blurple": discord.ButtonStyle.blurple,
        "primary": discord.ButtonStyle.primary,
        "secondary": discord.ButtonStyle.secondary,
        "link": discord.ButtonStyle.link,
        "url": discord.ButtonStyle.url,
        "red": discord.ButtonStyle.red,
        "danger": discord.ButtonStyle.danger,
        "green": discord.ButtonStyle.green,
        "success": discord.ButtonStyle.success,
        "grey": discord.ButtonStyle.grey,
        "gray": discord.ButtonStyle.gray,
    }
    if colour.lower() in valid_colours:
        return valid_colours[colour.lower()]
    raise ButtonColourNotFound(f'"{colour}" is not a valid button colour.')


async def pagify_this(
    big_ass_variable_string: str,
    delim: str,
    page_text: str = "Page ({index}/{pages})",
    page_char: int = 2000,
    is_embed: bool = True,
    embed_title: str = None,
    embed_colour: discord.Colour = None,
    embed_thumbnail: str = None,
    embed_image: str = None,
    embed_timestamp: datetime = None,
    footer_icon: str = None,
    author_icon: str = None,
    author_name: str = None,
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
                title=embed_title,
                colour=embed_colour,
                description=page,
                timestamp=embed_timestamp,
            )
            embed.set_footer(text=formatted_page_text, icon_url=footer_icon)
            embed.set_thumbnail(url=embed_thumbnail)
            embed.set_image(url=embed_image)
            embed.set_author(url=author_icon, name=author_name)
            final_page.append(embed)
        else:
            final_page.append(f"{page}\n\n{formatted_page_text}")

    return final_page
