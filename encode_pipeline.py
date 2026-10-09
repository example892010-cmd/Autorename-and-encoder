"""Automatic multi-resolution encoding pipeline for video uploads.

This runs before the legacy rename handler for video files, encodes each
configured resolution, and uploads each result as soon as that encode finishes.
Non-video documents and audio continue through the original rename handler.
"""
import asyncio
import os
import re
import time
import uuid
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import StopPropagation
from pyrogram.errors import UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

from config import Config
from helper.database import AshutoshGoswami24 as madflixbotz
from helper.utils import convert, humanbytes, progress_for_pyrogram

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".mpeg", ".mpg",
    ".ts", ".wmv", ".flv", ".3gp", ".ogv", ".vob", ".mts", ".m2ts"
}

# Limit parallel encode jobs to avoid exhausting small hosting instances.
_encode_semaphore = asyncio.Semaphore(max(1, int(os.environ.get("ENCODE_CONCURRENCY", "2"))))


def _season_from_name(name: str):
    match = re.search(r"\bS(\d+)(?=E|EP|\b)", name, re.IGNORECASE)
    return match.group(1) if match else "01"


def _title_from_name(name: str):
    stem = Path(name).stem
    match = re.search(r"\s+S\d+\b", stem, re.IGNORECASE)
    title = stem[:match.start()] if match else stem
    title = re.sub(r"[._]+", " ", title)
    title = re.sub(r"\s+", " ", title).strip(" -_")
    return title or "Unknown Title"


def _episode_from_name(name: str):
    patterns = [
        r"(?i)S\d{1,2}\s*(?:E|EP)\s*(\d{1,4})",
        r"(?i)\b(?:E|EP)\s*0*(\d{1,4})\b",
        r"(?i)\bEpisode\s*0*(\d{1,4})\b",
        r"(?:^|\s|[-_.])0*(\d{1,4})(?=\s|[-_.\[])"
    ]
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            return match.group(1)
    return None


def _build_output_name(template: str, original_name: str, resolution: int):
    stem = Path(original_name).stem
    episode = _episode_from_name(stem) or "01"
    season = _season_from_name(stem)
    title = _title_from_name(stem)
    quality = f"{resolution}p"
    result = template.replace("[episode]", "EP" + episode)
    # Support both the legacy tokens and brace-style tokens.
    replacements = {
        "{title}": title,
        "{episode}": episode,
        "{quality}": quality,
        "{season}": season,
        "episode": episode or "",
        "quality": quality,
        "Quality": quality,
        "QUALITY": quality,
    }
    for token, value in replacements.items():
        result = result.replace(token, value)
    result = re.sub(r"\s+", " ", result).strip(" .-_\t")
    result = re.sub(r'[\\/:*?"<>|]', "_", result)
    if not result:
        result = f"{stem} [{quality}]"
    return result + ".mp4"


def _probe_duration(path: str) -> int:
    try:
        metadata = extractMetadata(createParser(path))
        if metadata and metadata.has("duration"):
            return int(metadata.get("duration").seconds)
    except Exception:
        pass
    return 0


async def _encode_one(source: str, output: str, height: int, metadata_args=None):
    # Keep smaller sources at their native height rather than upscaling.
    vf = f"scale=-2:min({height}\\,ih)"
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", source,
        "-map", "0:v:0", "-map", "0:a?", "-sn", "-dn",
        "-vf", vf, "-c:v", "libx264", "-preset", os.environ.get("ENCODE_PRESET", "veryfast"),
        "-crf", os.environ.get("ENCODE_CRF", "24"), "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
    ]
    if metadata_args:
        command.extend(metadata_args)
    command.append(output)
    proc = await asyncio.create_subprocess_exec(
        *command, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0 or not os.path.isfile(output) or os.path.getsize(output) == 0:
        error = stderr.decode("utf-8", "replace")[-1200:]
        raise RuntimeError(error or f"FFmpeg failed for {height}p")
    return output


async def _metadata_arguments(user_id: int):
    """Return per-user metadata settings in FFmpeg argument form."""
    try:
        if not await madflixbotz.get_metadata(user_id):
            return []
        values = {
            "title": await madflixbotz.get_title(user_id),
            "author": await madflixbotz.get_author(user_id),
            "artist": await madflixbotz.get_artist(user_id),
            "audio": await madflixbotz.get_audio(user_id),
            "subtitle": await madflixbotz.get_subtitle(user_id),
            "video": await madflixbotz.get_video(user_id),
        }
        if not any(values.values()):
            values["title"] = await madflixbotz.get_metadata_code(user_id)
        args = []
        if values["title"]:
            args.extend(["-metadata", f"title={values['title']}"])
        if values["author"]:
            args.extend(["-metadata", f"author={values['author']}"])
        if values["artist"]:
            args.extend(["-metadata", f"artist={values['artist']}"])
        if values["video"]:
            args.extend(["-metadata:s:v", f"title={values['video']}"])
        if values["audio"]:
            args.extend(["-metadata:s:a", f"title={values['audio']}"])
        # This pipeline removes subtitle streams, so subtitle title is intentionally not applied.
        return args
    except Exception:
        return []


async def _upload_encoded(client, message: Message, output: str, display_name: str, thumb_id: str | None, duration: int):
    user_id = message.from_user.id
    caption_template = await madflixbotz.get_caption(user_id)
    size = os.path.getsize(output)
    caption = caption_template.format(
        filename=display_name,
        filesize=humanbytes(size),
        duration=convert(duration),
    ) if caption_template else f"**{display_name}**"

    thumb_path = None
    try:
        if thumb_id:
            thumb_path = await client.download_media(thumb_id)
            if thumb_path:
                with Image.open(thumb_path) as im:
                    im.convert("RGB").save(thumb_path, "JPEG")
        await client.send_video(
            chat_id=message.chat.id,
            video=output,
            caption=caption,
            thumb=thumb_path,
            duration=duration,
            supports_streaming=True,
        )
    finally:
        if thumb_path and os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except OSError:
                pass


@Client.on_message(filters.private & (filters.video | filters.document), group=-1)
async def encode_video_upload(client: Client, message: Message):
    """Encode incoming video media; let legacy handler process other files."""
    if not madflixbotz.is_configured:
        await message.reply_text("⚠️ Database is not configured. Please add DB_URL in Render → Environment.")
        raise StopPropagation
    if not message.from_user:
        return

    if message.video:
        original_name = message.video.file_name or f"video_{message.id}.mp4"
        file_id = message.video.file_id
    elif message.document:
        original_name = message.document.file_name or f"file_{message.id}"
        if Path(original_name).suffix.lower() not in VIDEO_EXTENSIONS:
            return
        file_id = message.document.file_id
    else:
        return

    user_id = message.from_user.id

    # Preserve the existing force-subscription gate for video uploads.
    required_channels = list(getattr(Config, "FORCE_SUB_CHANNELS", []) or [])
    single_channel = (getattr(Config, "FORCE_SUB", "") or "").strip()
    if single_channel:
        required_channels.append(single_channel)
    required_channels = list(dict.fromkeys(str(ch).strip().lstrip("@") for ch in required_channels if str(ch).strip()))
    missing_channels = []
    for channel in required_channels:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in (ChatMemberStatus.LEFT, ChatMemberStatus.BANNED):
                missing_channels.append(channel)
        except UserNotParticipant:
            missing_channels.append(channel)
        except Exception:
            # Don't block file processing if Telegram temporarily cannot verify membership.
            continue
    if missing_channels:
        buttons = [[InlineKeyboardButton(f"📢 Join {channel}", url=f"https://t.me/{channel}")]
                   for channel in missing_channels]
        await message.reply_text(
            "Please join the required channel(s) before using the bot.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        raise StopPropagation

    template = await madflixbotz.get_format_template(user_id)
    if not template:
        # Let the existing rename handler provide its normal setup message.
        return

    resolutions_text = getattr(Config, "ENCODE_RESOLUTIONS", os.environ.get("ENCODE_RESOLUTIONS", "480,720,1080"))
    resolutions = []
    for item in resolutions_text.split(","):
        try:
            value = int(item.strip().lower().replace("p", ""))
            if value in (240, 360, 480, 720, 1080, 1440, 2160) and value not in resolutions:
                resolutions.append(value)
        except ValueError:
            continue
    if not resolutions:
        resolutions = [480, 720, 1080]

    # Stop the old handler for this video so the original is not also uploaded.
    status = await message.reply_text(
        f"🎬 Starting automatic encoding: {', '.join(f'{x}p' for x in resolutions)}\n"
        "Each version will upload as soon as it finishes."
    )
    workdir = Path("downloads")
    workdir.mkdir(parents=True, exist_ok=True)
    unique = f"{user_id}_{message.id}_{uuid.uuid4().hex[:8]}"
    source = str(workdir / f"{unique}_source{Path(original_name).suffix or '.mp4'}")
    output_paths = []
    try:
        await client.download_media(
            message=message,
            file_name=source,
            progress=progress_for_pyrogram,
            progress_args=("⬇️ Downloading source...", status, time.time()),
        )
        duration = _probe_duration(source)
        thumb_id = await madflixbotz.get_thumbnail(user_id)
        metadata_args = await _metadata_arguments(user_id)

        async def encode_and_upload(height):
            async with _encode_semaphore:
                output_name = _build_output_name(template, original_name, height)
                output = str(workdir / f"{unique}_{height}p_{Path(output_name).name}")
                output_paths.append(output)
                await _encode_one(source, output, height, metadata_args)
                # Use the exact final output name in Telegram's filename metadata.
                await _upload_encoded(client, message, output, output_name, thumb_id, duration)
                return height

        tasks = [asyncio.create_task(encode_and_upload(height)) for height in resolutions]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        succeeded = [str(r) + "p" for r in results if not isinstance(r, Exception)]
        failed = [f"{resolutions[i]}p: {r}" for i, r in enumerate(results) if isinstance(r, Exception)]
        lines = ["✅ Encoding finished."]
        if succeeded:
            lines.append("Uploaded: " + ", ".join(succeeded))
        if failed:
            lines.append("Failed: " + "; ".join(failed))
        await status.edit_text("\n".join(lines))
    except Exception as exc:
        await status.edit_text(f"❌ Encoding failed: {str(exc)[:900]}")
    finally:
        for path in [source, *output_paths]:
            try:
                if path and os.path.isfile(path):
                    os.remove(path)
            except OSError:
                pass
    raise StopPropagation
