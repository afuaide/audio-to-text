"""音频下载模块：支持视频平台链接和直链音频"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

VIDEO_PLATFORM_PATTERNS = [
    r"(youtube\.com|youtu\.be)",
    r"bilibili\.com",
    r"douyin\.com",
    r"tiktok\.com",
    r"twitter\.com|x\.com",
    r"vimeo\.com",
]

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac", ".wma", ".opus", ".webm"}


def is_video_platform(url: str) -> bool:
    for pattern in VIDEO_PLATFORM_PATTERNS:
        if re.search(pattern, url):
            return True
    return False


def is_direct_audio(url: str) -> bool:
    path = urlparse(url).path.lower()
    return any(path.endswith(ext) for ext in AUDIO_EXTENSIONS)


def find_yt_dlp() -> str:
    found = shutil.which("yt-dlp")
    if found:
        return found
    if sys.platform == "win32":
        user_scripts = (
            Path.home() / "AppData" / "Roaming" / "Python"
            / f"Python{sys.version_info.major}{sys.version_info.minor}"
            / "Scripts" / "yt-dlp.exe"
        )
        if user_scripts.exists():
            return str(user_scripts)
    raise FileNotFoundError("找不到 yt-dlp，请运行: pip install yt-dlp")


def find_ffmpeg() -> str | None:
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        ffmpeg_dir = Path(ffmpeg_path).parent
        standard_name = ffmpeg_dir / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        if not standard_name.exists():
            shutil.copy2(ffmpeg_path, standard_name)
        return str(standard_name)
    except ImportError:
        return None


def download_from_platform(url: str, output_dir: str) -> str:
    yt_dlp = find_yt_dlp()
    print(f"[下载] 从视频平台提取音频: {url}")
    output_template = os.path.join(output_dir, "audio.%(ext)s")
    cmd = [
        yt_dlp,
        "-x",
        "--audio-format", "mp3",
        "-o", output_template,
        "--no-playlist",
        url,
    ]
    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        cmd.insert(-1, "--ffmpeg-location")
        cmd.insert(-1, str(Path(ffmpeg_path).parent))
    subprocess.run(cmd, check=True)
    for f in os.listdir(output_dir):
        if f.startswith("audio."):
            return os.path.join(output_dir, f)
    raise FileNotFoundError("yt-dlp 下载完成但未找到输出文件")


def download_direct(url: str, output_path: str) -> str:
    print(f"[下载] 直接下载音频: {url}")
    resp = requests.get(url, stream=True, timeout=120, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r  进度: {pct:.1f}% ({downloaded // 1024}KB / {total // 1024}KB)", end="", flush=True)

    print()
    return output_path


def _cleanup_audio_files(output_dir: str) -> None:
    for f in os.listdir(output_dir):
        if f.startswith("audio."):
            os.remove(os.path.join(output_dir, f))


def download_audio(url: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)

    if is_video_platform(url):
        return download_from_platform(url, output_dir)

    if is_direct_audio(url):
        ext = Path(urlparse(url).path).suffix
        output_path = os.path.join(output_dir, f"audio{ext}")
        return download_direct(url, output_path)

    try:
        return download_from_platform(url, output_dir)
    except Exception as e:
        print(f"[提示] yt-dlp 尝试失败 ({e})，将尝试直接下载")
        _cleanup_audio_files(output_dir)

    output_path = os.path.join(output_dir, "audio.mp3")
    return download_direct(url, output_path)
