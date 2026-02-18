# -*- coding: utf-8 -*-
import json
import os
import urllib.error
import urllib.request


class OpenAIResponsesClient:
    def __init__(self, api_key, model="gpt-5.2", timeout=120):
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def _extract_text(self, payload):
        text = payload.get("output_text")
        if text:
            return text.strip()

        output = payload.get("output", [])
        chunks = []
        for item in output:
            for content in item.get("content", []):
                if content.get("type") == "output_text" and content.get("text"):
                    chunks.append(content["text"])
                elif content.get("type") == "text" and content.get("text"):
                    chunks.append(content["text"])
        return "\n".join(chunks).strip()

    def generate(self, system_prompt, user_prompt):
        body = {
            "model": self.model,
            "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
            ],
        }

        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as res:
                payload = json.loads(res.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenAI API error: {e.code} {detail}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"OpenAI API connection error: {e}") from e

        text = self._extract_text(payload)
        if not text:
            raise RuntimeError("OpenAI API returned empty text")
        return text


class Agent:
    def __init__(self, name, profile_path, client):
        self.name = name
        self.profile_path = profile_path
        self.client = client
        self.profile_text = self._load_profile()

    def _load_profile(self):
        with open(self.profile_path, "r", encoding="utf-8") as f:
            return f.read()

    def _system_prompt(self):
        return (
            "あなたは次の哲学者本人として発言する。\n"
            f"名前: {self.name}\n"
            "以下は自己紹介プロフィールであり、人格・語彙・立場の根拠とする。\n"
            "--- PROFILE START ---\n"
            f"{self.profile_text}\n"
            "--- PROFILE END ---\n"
            "制約:\n"
            "- 日本語で出力\n"
            "- 1ターンの発話は2〜5文\n"
            "- 相手の直前発言に反応する\n"
            "- 人格を崩さない\n"
            "- 箇条書きを使わない\n"
        )

    def first_turn(self):
        user_prompt = (
            "1on1議論の先手として、最初に『議題: ...』を1行で宣言し、その後に主張本文を続けて出力せよ。"
            "議題は構造主義に関係する具体的論点にすること。"
        )
        return self.client.generate(self._system_prompt(), user_prompt)

    def turn(self, topic, transcript_text):
        user_prompt = (
            f"現在の議題: {topic}\n"
            "ここまでの議論ログを踏まえて次の1ターン発話を作成せよ。\n"
            "--- LOG START ---\n"
            f"{transcript_text}\n"
            "--- LOG END ---"
        )
        return self.client.generate(self._system_prompt(), user_prompt)

    def judge_loser(self, topic, transcript_text, debater_a, debater_b):
        user_prompt = (
            "あなたは見物者として敗者を1名だけ決める。\n"
            f"議題: {topic}\n"
            f"対戦者A: {debater_a}\n"
            f"対戦者B: {debater_b}\n"
            "判断対象ログ:\n"
            "--- LOG START ---\n"
            f"{transcript_text}\n"
            "--- LOG END ---\n"
            "出力形式を厳守:\n"
            "敗者: <対戦者Aまたは対戦者Bの名前>\n"
            "理由: <1〜3文>"
        )
        return self.client.generate(self._system_prompt(), user_prompt)


def build_client_from_env():
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.2")
    timeout = int(os.getenv("OPENAI_TIMEOUT_SEC", "120"))
    return OpenAIResponsesClient(api_key=api_key, model=model, timeout=timeout)
