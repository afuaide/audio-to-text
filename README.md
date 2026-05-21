# audio-to-text-cli

音频下载 + 语音转文字命令行工具。

给一个链接，自动下载音频并转录为文字。支持多语言自动识别，中文支持简繁体切换。

## 支持的音频来源

| 来源 | 示例 |
|------|------|
| **Bilibili** | `https://www.bilibili.com/video/BVxxxxx` |
| **YouTube** | `https://www.youtube.com/watch?v=xxxxx` |
| **抖音** | `https://www.douyin.com/video/xxxxx` |
| **TikTok** | `https://www.tiktok.com/@user/video/xxxxx` |
| **Twitter/X** | `https://x.com/user/status/xxxxx` |
| **Vimeo** | `https://vimeo.com/xxxxx` |
| **直链音频** | `https://example.com/audio.mp3` |
| **其他** | 任何 yt-dlp 支持的平台 |

## 系统要求

- **Python 3.10+**（唯一前置条件）
- 无需单独安装 FFmpeg — 依赖包自带
- 无需 C/C++ 编译器 — 所有依赖均有预编译包

### 支持的操作系统

| 平台 | 架构 | 支持 |
|------|------|------|
| Windows | x86-64 | ✅ |
| Linux | x86-64 | ✅ |
| Linux | ARM64 | ✅ |
| macOS | Intel (x86-64) | ✅ |
| macOS | Apple Silicon (M系列) | ✅ |

### GPU 加速（可选）

默认使用 CPU 运行，无需额外配置。如需 GPU 加速，需安装：
- NVIDIA CUDA 12
- cuDNN 9 for CUDA 12

## 安装

从 PyPI 安装：

```bash
pip install audio-to-text-cli
```

安装后如果提示 `audio-to-text` 命令找不到，可以用 `python -m audio_to_text.cli` 代替，或将 Python Scripts 目录加入系统 PATH。

或从源码安装：

```bash
git clone https://github.com/afuaide/audio-to-text-cli.git
cd audio-to-text-cli
pip install -e .
```

## 使用方法

安装后会注册 `audio-to-text` 命令：

```bash
# 基本用法 — 自动检测语言，中文默认输出简体
audio-to-text "https://www.bilibili.com/video/BV1wqLV6JEga/"

# 用较小的模型（更快，精度稍低）
audio-to-text -m small "https://www.youtube.com/watch?v=xxxxx"

# 指定语言（跳过自动检测，更快）
audio-to-text -l zh "URL"

# 输出到文件
audio-to-text -o result.txt "URL"

# 中文输出繁体
audio-to-text -c traditional "URL"

# 中文不做简繁转换，保留模型原始输出
audio-to-text -c raw "URL"

# 保留下载的音频文件
audio-to-text --keep-audio "URL"

# 指定音频下载目录
audio-to-text -d ./downloads "URL"
```

也可以通过 `python -m` 运行：

```bash
python -m audio_to_text.cli "URL"
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 音频URL或视频平台链接 | 必填 |
| `-m, --model` | Whisper 模型大小: `tiny` / `base` / `small` / `medium` / `large-v3` | `large-v3` |
| `-l, --language` | 语言代码 (`zh` 中文, `en` 英语, `ja` 日语, `ko` 韩语 等) | 自动检测 |
| `-c, --chinese` | 中文输出格式: `simplified`(简体) / `traditional`(繁体) / `raw`(不转换) | `simplified` |
| `-o, --output` | 转录结果保存路径 | 终端输出 |
| `-d, --download-dir` | 音频下载目录 | 临时目录 |
| `--keep-audio` | 保留下载的音频文件 | 否 |

## 模型选择

| 模型 | 大小 | 速度 | 精度 | 建议场景 |
|------|------|------|------|----------|
| `tiny` | ~75MB | 极快 | 一般 | 快速预览 |
| `base` | ~150MB | 很快 | 尚可 | 日常使用 |
| `small` | ~500MB | 快 | 较好 | 推荐起步 |
| `medium` | ~1.5GB | 中等 | 很好 | 精度优先 |
| `large-v3` | ~3GB | 较慢 | 最佳 | 追求最高精度 |

首次使用某个模型会自动从 HuggingFace 下载，之后会缓存到本地。

## 依赖说明

| 依赖 | 作用 |
|------|------|
| `yt-dlp` | 从视频平台提取音频 |
| `faster-whisper` | 语音转文字引擎（本地离线运行） |
| `requests` | 下载直链音频 |
| `imageio-ffmpeg` | 自带 ffmpeg，用于音频格式转换 |
| `opencc-python-reimplemented` | 中文简繁体转换 |

所有依赖通过 `pip install` 安装，无需额外安装系统软件。
