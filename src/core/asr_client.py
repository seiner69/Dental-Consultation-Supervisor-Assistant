import time
import logging
import os
import json
import requests
import oss2
import dashscope
from dashscope.audio.asr import Transcription
from http import HTTPStatus
from config.settings import settings

logger = logging.getLogger(__name__)

class ASRClient:
    def __init__(self):
        dashscope.api_key = settings.DASHSCOPE_API_KEY
        self.auth = oss2.Auth(settings.OSS_ACCESS_KEY_ID, settings.OSS_ACCESS_KEY_SECRET)
        self.bucket = oss2.Bucket(self.auth, settings.OSS_ENDPOINT, settings.OSS_BUCKET_NAME)

    def _upload_to_oss(self, file_path: str) -> str | None:
        if not os.path.exists(file_path):
            return None

        file_name = os.path.basename(file_path)
        object_key = f"recordings/{int(time.time())}_{file_name}"
        ext = os.path.splitext(file_path)[-1].lower()
        mime_map = {'.m4a': 'audio/mp4', '.mp3': 'audio/mpeg', '.wav': 'audio/wav'}
        content_type = mime_map.get(ext, 'application/octet-stream')
        headers = {'Content-Type': content_type}

        with open(file_path, "rb") as f:
            self.bucket.put_object(object_key, f, headers=headers)

        return self.bucket.sign_url('GET', object_key, 3600)

    def _format_dialogue(self, data: dict) -> str:
        """完全复刻 cee.py 的 _extract_dialogue_from_data"""
        sentences = []
        if 'transcripts' in data and data['transcripts']:
            sentences = data['transcripts'][0].get('sentences', [])
        elif 'results' in data and data['results']:
            sentences = data['results'][0].get('sentences', [])

        if not sentences:
            if 'transcripts' in data and data['transcripts']:
                return data['transcripts'][0].get('text', '')
            elif 'results' in data and data['results']:
                return data['results'][0].get('text', '')
            return "（未识别到有效内容）"

        dialogue_lines = []
        current_speaker = None
        current_text = []

        for sent in sentences:
            speaker_id = sent.get('speaker_id', 0)
            text = sent.get('text', '')
            if speaker_id != current_speaker:
                if current_speaker is not None:
                    dialogue_lines.append(f"【说话人 {current_speaker}】: {''.join(current_text)}")
                current_speaker = speaker_id
                current_text = [text]
            else:
                current_text.append(text)

        if current_speaker is not None:
            dialogue_lines.append(f"【说话人 {current_speaker}】: {''.join(current_text)}")

        return "\n\n".join(dialogue_lines)

    def transcribe(self, audio_path: str) -> str:
        if not os.path.exists(audio_path):
            return "Error: 文件不存在"

        file_url = self._upload_to_oss(audio_path)
        if not file_url:
            return "Error: OSS 上传失败"

        try:
            logger.info("🚀 提交转写任务 (paraformer-v1 + 角色分离)...")
            job = Transcription.async_call(
                model='paraformer-v1',
                file_urls=[file_url],
                language_hints=['zh', 'en'],
                diarization_enabled=True,
                speaker_count=2
            )

            if job.status_code != HTTPStatus.OK:
                return f"Error: 提交失败 - {job.message}"

            task_id = job.output.task_id
            logger.info(f"任务已提交: {task_id}")

            while True:
                response = Transcription.fetch(task=task_id)
                status = getattr(response.output, 'task_status', 'UNKNOWN')

                if status == 'SUCCEEDED':
                    logger.info("🎉 转写成功，解析结果...")
                    try:
                        raw = json.loads(json.dumps(response.output, default=lambda o: o.__dict__))
                    except:
                        raw = response.output

                    if 'results' in raw and raw['results']:
                        first = raw['results'][0]
                        if 'transcription_url' in first and first['transcription_url']:
                            try:
                                r = requests.get(first['transcription_url'])
                                r.raise_for_status()
                                return self._format_dialogue(r.json())
                            except Exception as e:
                                return f"Error: 下载结果失败 - {e}"

                    return self._format_dialogue(raw)

                if status == 'FAILED':
                    return f"Error: ASR 失败 - {response.output.message}"

                time.sleep(2)

        except Exception as e:
            logger.error(f"SDK Error: {e}")
            return f"Error: 系统异常 - {e}"
