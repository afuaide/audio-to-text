"""CLI 入口"""

import argparse
import io
import os
import shutil
import sys
import tempfile

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from audio_to_text.downloader import download_audio
from audio_to_text.transcriber import transcribe


def main():
    parser = argparse.ArgumentParser(
        prog="audio-to-text",
        description="音频下载 + 语音转文字工具 — 支持 B站/YouTube 等视频平台及直链音频",
    )
    parser.add_argument("url", help="音频URL(直链)或视频平台链接(B站/YouTube等)")
    parser.add_argument(
        "-m", "--model", default="large-v3",
        choices=["tiny", "base", "small", "medium", "large-v3"],
        help="Whisper 模型大小 (默认: large-v3)",
    )
    parser.add_argument("-l", "--language", default=None, help="指定语言代码 (如 zh/en/ja/ko)，不指定则自动检测")
    parser.add_argument("-o", "--output", default=None, help="转录结果输出文件路径 (默认: 输出到终端)")
    parser.add_argument("-d", "--download-dir", default=None, help="音频下载目录 (默认: 临时目录)")
    parser.add_argument("--keep-audio", action="store_true", help="保留下载的音频文件")
    parser.add_argument(
        "-c", "--chinese", default="simplified",
        choices=["simplified", "traditional", "raw"],
        help="中文输出格式: simplified(简体,默认) / traditional(繁体) / raw(原始不转换)",
    )

    args = parser.parse_args()

    if args.download_dir:
        download_dir = args.download_dir
        cleanup = False
    elif args.keep_audio:
        download_dir = os.path.join(os.getcwd(), "audio_downloads")
        cleanup = False
    else:
        download_dir = tempfile.mkdtemp(prefix="transcriber_")
        cleanup = True

    try:
        audio_path = download_audio(args.url, download_dir)
        print(f"[完成] 音频文件: {audio_path}")

        chinese = None if args.chinese == "raw" else args.chinese
        text = transcribe(audio_path, model_size=args.model, language=args.language, chinese=chinese)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"\n[完成] 转录结果已保存到: {args.output}")
        else:
            print(f"\n{'=' * 60}")
            print("转录结果:")
            print(f"{'=' * 60}")
            print(text)

    except KeyboardInterrupt:
        print("\n[中断] 用户取消操作")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n[错误] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[错误] {e}")
        sys.exit(1)
    finally:
        if cleanup and os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
            print("[清理] 已删除临时文件")


if __name__ == "__main__":
    main()
