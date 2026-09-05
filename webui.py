"""Audio Separator Web UI (Gradio).

本地 Web 界面：上传音频 -> 选择模型 -> 一键分离 -> 下载人声/伴奏等音轨。
依赖项目内已配置好的 .venv 环境（含 GPU 加速与完整版 ffmpeg）。

启动方式：
    & ".\.venv\Scripts\python.exe" webui.py
然后浏览器打开终端提示的本地地址（默认 http://127.0.0.1:7860）。
"""

import os
import tempfile
import uuid

import gradio as gr

from audio_separator.separator import Separator

# 与项目环境一致的模型缓存目录
MODEL_DIR = "/tmp/audio-separator-models/"
DEFAULT_MODEL = "model_bs_roformer_ep_317_sdr_12.9755.ckpt"

# 输出格式可选
OUTPUT_FORMATS = ["WAV", "FLAC", "MP3", "OGG", "M4A", "ALAC"]

# 常见音轨名（用于"只输出单个音轨"下拉框）
STEM_CHOICES = ["全部音轨", "Vocals", "Instrumental", "Drums", "Bass", "Other", "Guitar", "Piano"]


def _build_model_choices():
    """返回模型文件名列表，按名称排序。"""
    try:
        sep = Separator(model_file_dir=MODEL_DIR, info_only=True)
        simplified = sep.list_supported_model_files()
        files = sorted(f for f in simplified.keys())
        # 确保默认模型在列表中
        return files if DEFAULT_MODEL in files else [DEFAULT_MODEL] + files
    except Exception as e:  # noqa: BLE001
        print(f"加载模型列表失败，使用默认模型: {e}")
        return [DEFAULT_MODEL]


def separate_audio(
    input_file,
    model_filename,
    output_format,
    single_stem,
    chunk_duration,
    progress=gr.Progress(track_tqdm=True),
):
    """执行分离并返回输出文件列表。"""
    if input_file is None:
        raise gr.Error("请先上传一个音频文件。")

    src_path = input_file
    # Gradio 上传的文件可能是临时文件，确保是可读的绝对路径
    if not os.path.exists(src_path):
        raise gr.Error(f"找不到上传的文件: {src_path}")

    # 单个 stem 参数映射
    single_stem_val = None if single_stem == "全部音轨" else single_stem

    # 输出到独立临时目录，避免污染项目目录，也便于清理
    out_dir = tempfile.mkdtemp(prefix="audio_sep_out_")

    progress(0.05, desc="初始化分离器…")
    separator = Separator(
        model_file_dir=MODEL_DIR,
        output_dir=out_dir,
        output_format=output_format,
        output_single_stem=single_stem_val,
        chunk_duration=chunk_duration if chunk_duration and chunk_duration > 0 else None,
    )

    progress(0.15, desc=f"加载模型 {model_filename}…")
    separator.load_model(model_filename=model_filename)

    progress(0.3, desc="开始分离…")
    output_files = separator.separate(src_path)

    if not output_files:
        raise gr.Error("分离未产生任何输出文件，请查看日志。")

    # separator.separate 返回的是相对文件名，改为绝对路径以便 Gradio 下载
    output_files = [f if os.path.isabs(f) else os.path.join(out_dir, f) for f in output_files]

    progress(1.0, desc="完成")
    return output_files


def build_ui():
    model_choices = _build_model_choices()

    with gr.Blocks(title="Audio Separator Web UI", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            "# 🎵 Audio Separator Web UI\n"
            "基于 `python-audio-separator` 的本地音频分离界面。上传音频，选择模型，即可分离人声与伴奏。"
        )

        with gr.Row():
            with gr.Column(scale=1):
                input_file = gr.File(
                    label="上传音频文件",
                    file_types=["audio", ".wav", ".flac", ".mp3", ".ogg", ".opus", ".m4a", ".aiff", ".ac3"],
                )
                model = gr.Dropdown(
                    choices=model_choices,
                    value=DEFAULT_MODEL if DEFAULT_MODEL in model_choices else model_choices[0],
                    label="分离模型",
                )
                fmt = gr.Dropdown(choices=OUTPUT_FORMATS, value="FLAC", label="输出格式")
                stem = gr.Dropdown(choices=STEM_CHOICES, value="全部音轨", label="输出音轨")
                chunk = gr.Slider(
                    minimum=0,
                    maximum=1200,
                    step=60,
                    value=0,
                    label="分块时长（秒，0=不分块；长音频建议 300-600）",
                )
                run_btn = gr.Button("开始分离", variant="primary", size="lg")

            with gr.Column(scale=1):
                outputs = gr.Files(label="分离结果（可下载）")
                status = gr.Markdown("等待上传并开始分离…")

        run_btn.click(
            separate_audio,
            inputs=[input_file, model, fmt, stem, chunk],
            outputs=[outputs],
        ).then(
            lambda: "✅ 分离完成，请下载右侧音轨文件。",
            outputs=[status],
        )

        gr.Markdown(
            "> 提示：首次使用某个模型时会自动从 HuggingFace 下载（模型缓存于 `%s`）。"
            " 本机已启用 GPU 加速（RTX 4080）与完整版 ffmpeg。" % MODEL_DIR
        )

    return demo


if __name__ == "__main__":
    app = build_ui()
    app.launch(server_name="127.0.0.1", server_port=7860, show_error=True, prevent_thread_lock=False)