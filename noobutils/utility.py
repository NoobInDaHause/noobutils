import discord
import pathlib

from redbot.core.bot import app_commands, commands, Red
from redbot.core.errors import CogLoadError
from redbot.core.utils import (
    chat_formatting as cf,
    get_end_user_data_statement_or_raise,
)

from datetime import datetime
from discord.ext import tasks
from packaging import version
from typing import Union, List, Literal

from . import __version__
from .converters import NoobCoordinate
from .exceptions import ButtonColourNotFound, MemberOrGuildNotFound


Application_Group = app_commands.Group
Context = commands.Context
Interaction = discord.Interaction[Red]

command = commands.command
group = commands.group
hybrid_command = commands.hybrid_command
hybrid_group = commands.hybrid_group
app_command = app_commands.command
loop = tasks.loop
listener = commands.Cog.listener


def get_eud(file: Union[pathlib.Path, str]) -> str:
    return get_end_user_data_statement_or_raise(file)


def is_have_avatar(
    thing: Union[
        discord.Member, discord.User, discord.Guild, discord.ClientUser
    ] = None,
    display_av: bool = False,
) -> str:
    if thing is None:
        return ""
    elif isinstance(thing, (discord.Member, discord.ClientUser, discord.User)):
        return (
            thing.display_avatar.url
            if display_av
            else (
                thing.avatar.url
                if thing.avatar
                else thing.display_avatar.url if thing.display_avatar else ""
            )
        )
    elif isinstance(thing, discord.Guild):
        return thing.icon.url if thing.icon else ""
    else:
        raise MemberOrGuildNotFound(f'Member or Guild "{thing}" was not found.')


def access_denied(text_only: bool = False) -> str:
    return (
        "Access Denied."
        if text_only
        else (
            "[Access Denied.](https://cdn.discordapp.com/attachments/1000751975308197918/"
            "1110013262835228814/1.mp4)"
        )
    )


def get_button_colour(
    colour: Literal[
        "blurple",
        "primary",
        "secondary",
        "link",
        "url",
        "red",
        "danger",
        "green",
        "success",
        "grey",
        "gray",
    ]
) -> discord.ButtonStyle:
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


def pagify_this(
    big_ass_variable_string: str,
    delims: List[str] = None,
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
    if delims is None:
        delims = ["\n"]
    final_page = []
    page_length = page_char if is_embed else (page_char - 50)
    pages = list(
        cf.pagify(big_ass_variable_string, delims=delims, page_length=page_length)
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
            if embed_thumbnail:
                embed.set_thumbnail(url=embed_thumbnail)
            if embed_image:
                embed.set_image(url=embed_image)
            if author_name:
                embed.set_author(url=author_icon, name=author_name)
            final_page.append(embed)
        else:
            final_page.append(f"{page}\n\n{formatted_page_text}")

    return final_page


def version_check(needed_version: str):
    if version.parse(__version__) < version.parse(needed_version):
        raise CogLoadError(
            "This cog requires a newer version of noobutils.\n"
            f"Your system currently has noobutils version: **{__version__}**\n"
            f"The cog requires noobutils version: **{needed_version}** or newer\n"
            "Please run the command `[p]pipinstall --force-reinstall --no-cache-dir "
            "git+https://github.com/NoobInDaHause/noobutils.git` then restart your bot and load the cog."
            "\nIf the problem still continues, please report it to the cog author via [GitHub]"
            "(https://github.com/NoobInDaHause/noobutils) or join the Discord server [here](https://"
            "discord.gg/Hs2H9sQejw)."
        )
