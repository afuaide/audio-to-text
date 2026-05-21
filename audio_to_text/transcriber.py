"""语音转文字模块：基于 faster-whisper"""

from faster_whisper import WhisperModel
from opencc import OpenCC


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def make_converter(chinese: str | None) -> OpenCC | None:
    mapping = {
        "simplified": "t2s",
        "traditional": "s2tw",
    }
    config = mapping.get(chinese)
    if config:
        return OpenCC(config)
    return None


def transcribe(
    audio_path: str,
    model_size: str = "large-v3",
    language: str | None = None,
    chinese: str | None = None,
) -> str:
    print(f"[转录] 加载模型: {model_size}")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("[转录] 开始转录...")
    segments, info = model.transcribe(audio_path, language=language, beam_size=5)
    print(f"[转录] 检测到语言: {info.language} (置信度: {info.language_probability:.2f})")

    converter = None
    if info.language == "zh":
        converter = make_converter(chinese)
        if converter:
            label = "简体" if chinese == "simplified" else "繁体"
            print(f"[转录] 中文转换: -> {label}")

    lines = []
    for seg in segments:
        text = seg.text.strip()
        if converter:
            text = converter.convert(text)
        timestamp = f"[{format_time(seg.start)} -> {format_time(seg.end)}]"
        lines.append(f"{timestamp}  {text}")
        print(f"  {timestamp}  {text}")

    return "\n".join(lines)
