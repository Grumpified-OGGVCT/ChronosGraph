"""Media Handler — yt-dlp wrapper and FFmpeg chunking."""

import asyncio
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from config import settings

logger = logging.getLogger("chronosgraph.media")


@dataclass
class TextChunk:
    index: int
    start_time: str
    end_time: str
    text: str


@dataclass
class AudioChunk:
    index: int
    start_time: str
    file_path: str


def _seconds_to_hms(seconds: float) -> str:
    h, m, s = int(seconds // 3600), int((seconds % 3600) // 60), int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


async def download_video(url: str) -> Optional[str]:
    output_dir = settings.resolve_path(settings.video_cache_dir)
    cmd = ["yt-dlp", "-o", str(output_dir / "%(id)s.%(ext)s"),
           "--no-playlist", "--merge-output-format", "mp4", "--", url]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error("yt-dlp failed: %s", stderr.decode()[:500])
            return None
        for f in output_dir.iterdir():
            if f.suffix in (".mp4", ".mkv", ".webm"):
                return str(f)
    except FileNotFoundError:
        logger.error("yt-dlp not found on PATH")
    return None


async def get_video_title(url: str) -> str:
    try:
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "--get-title", "--no-playlist", "--", url,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        return stdout.decode().strip() or "Untitled"
    except Exception:
        return "Untitled"


async def extract_subtitles(url: str) -> Optional[str]:
    output_dir = settings.resolve_path(settings.audio_cache_dir)
    cmd = ["yt-dlp", "--write-auto-sub", "--sub-lang", "en", "--skip-download",
           "--write-sub", "--sub-format", "vtt", "-o", str(output_dir / "%(id)s"),
           "--no-playlist", "--", url]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
        for f in output_dir.iterdir():
            if f.suffix == ".vtt":
                text = _parse_vtt(f.read_text(encoding="utf-8", errors="replace"))
                f.unlink()
                if text and len(text.strip()) > 50:
                    return text
    except Exception as e:
        logger.warning("Subtitle extraction failed: %s", e)
    return None


def _parse_vtt(vtt_content: str) -> str:
    lines = vtt_content.split("\n")
    result = []
    ts_pattern = re.compile(r"(\d{2}:\d{2}:\d{2})\.\d{3}\s*-->")
    current_time = ""
    for line in lines:
        line = line.strip()
        ts_match = ts_pattern.match(line)
        if ts_match:
            current_time = ts_match.group(1)
        elif line and not line.startswith("WEBVTT") and not line.startswith("Kind:"):
            clean = re.sub(r"<[^>]+>", "", line)
            if clean and (not result or result[-1] != f"[{current_time}] {clean}"):
                result.append(f"[{current_time}] {clean}")
    return "\n".join(result)


async def extract_audio(video_path: str) -> Optional[str]:
    audio_dir = settings.resolve_path(settings.audio_cache_dir)
    output_full = str(audio_dir / Path(video_path).with_suffix(".wav").name)
    cmd = ["ffmpeg", "-y", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
           "-ar", "16000", output_full]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error("FFmpeg failed: %s", stderr.decode()[:300])
            return None
        return output_full
    except FileNotFoundError:
        logger.error("FFmpeg not found on PATH")
    return None


def chunk_text(text: str, chunk_minutes: int = 15, overlap_seconds: int = 30) -> list[TextChunk]:
    lines = text.split("\n")
    ts_pattern = re.compile(r"\[(\d{2}):(\d{2}):(\d{2})\]")
    timed = []
    for line in lines:
        m = ts_pattern.match(line)
        if m:
            secs = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            timed.append((secs, line))
        elif timed:
            timed[-1] = (timed[-1][0], timed[-1][1] + " " + line)
    if not timed:
        return [TextChunk(index=i, start_time="00:00:00", end_time="00:00:00",
                          text=text[i*5000:(i+1)*5000])
                for i in range(0, max(1, len(text) // 5000))]
    dur = chunk_minutes * 60
    chunks, start = [], 0.0
    while start < timed[-1][0]:
        end = start + dur
        cl = [l for t, l in timed if (start - overlap_seconds) <= t < end]
        if cl:
            chunks.append(TextChunk(index=len(chunks), start_time=_seconds_to_hms(start),
                                    end_time=_seconds_to_hms(min(end, timed[-1][0])),
                                    text="\n".join(cl)))
        start = end
    return chunks


async def chunk_audio(audio_path: str, chunk_minutes: int = 10) -> list[AudioChunk]:
    audio_dir = settings.resolve_path(settings.audio_cache_dir)
    base = Path(audio_path).stem
    seg = chunk_minutes * 60
    cmd = ["ffmpeg", "-y", "-i", audio_path, "-f", "segment",
           "-segment_time", str(seg), "-c", "copy",
           str(audio_dir / f"{base}_chunk_%03d.wav")]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()
    except FileNotFoundError:
        return []
    chunks, idx = [], 0
    while True:
        p = str(audio_dir / f"{base}_chunk_{idx:03d}.wav")
        if os.path.exists(p):
            chunks.append(AudioChunk(index=idx, start_time=_seconds_to_hms(idx * seg), file_path=p))
            idx += 1
        else:
            break
    return chunks


async def cleanup_audio(video_id: str) -> None:
    audio_dir = settings.resolve_path(settings.audio_cache_dir)
    for f in audio_dir.iterdir():
        if video_id in f.name and f.suffix == ".wav":
            f.unlink()


async def expand_playlist(url: str) -> list[dict]:
    import json
    cmd = ["yt-dlp", "--flat-playlist", "--dump-json", "--", url]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        entries = []
        for line in stdout.decode().strip().split("\n"):
            if line:
                e = json.loads(line)
                entries.append({"url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id','')}",
                                "title": e.get("title", "Untitled"),
                                "upload_date": e.get("upload_date", "")})
        entries.sort(key=lambda x: x.get("upload_date", ""))
        return entries
    except Exception as e:
        logger.error("Playlist expansion failed: %s", e)
        return []
