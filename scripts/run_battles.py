# -*- coding: utf-8 -*-
import os
import random

AGENTS = [
    {
        "id": "levi",
        "name": "クロード・レヴィ＝ストロース",
        "voice": [
            "私は比較の方法から語る。",
            "神話は差異の変換だ。",
            "交換の規則こそが文化を支える。",
            "構造は固定ではなく変換の規則である。",
        ],
        "strengths": {
            "神話": 3,
            "親族": 3,
            "構造": 2,
            "歴史": 1,
            "権力": 1,
            "主体": 1,
            "言語": 2,
            "イデオロギー": 1,
        },
    },
    {
        "id": "lacan",
        "name": "ジャック・ラカン",
        "voice": [
            "無意識は言語のように構造化されている。",
            "主体は裂け目として現れる。",
            "他者の欲望が主体を駆動する。",
            "象徴界の網が主体を規定する。",
        ],
        "strengths": {
            "神話": 1,
            "親族": 1,
            "構造": 2,
            "歴史": 1,
            "権力": 1,
            "主体": 3,
            "言語": 3,
            "イデオロギー": 1,
        },
    },
    {
        "id": "foucault",
        "name": "ミシェル・フーコー",
        "voice": [
            "権力は関係として遍在する。",
            "言説は真理を生産する。",
            "主体は歴史的に形成される。",
            "規律は身体を編成する。",
        ],
        "strengths": {
            "神話": 1,
            "親族": 1,
            "構造": 2,
            "歴史": 3,
            "権力": 3,
            "主体": 2,
            "言語": 2,
            "イデオロギー": 1,
        },
    },
    {
        "id": "althusser",
        "name": "ルイ・アルチュセール",
        "voice": [
            "構造的因果性を見よ。",
            "イデオロギーは主体を呼びかける。",
            "歴史は過剰決定されている。",
            "理論の精度が政治を支える。",
        ],
        "strengths": {
            "神話": 1,
            "親族": 1,
            "構造": 2,
            "歴史": 2,
            "権力": 2,
            "主体": 2,
            "言語": 1,
            "イデオロギー": 3,
        },
    },
    {
        "id": "barthes",
        "name": "ロラン・バルト",
        "voice": [
            "記号は日常の神話を作る。",
            "作者の死は読者の誕生だ。",
            "テクストの快楽を忘れるな。",
            "意味は多声的に開かれる。",
        ],
        "strengths": {
            "神話": 2,
            "親族": 1,
            "構造": 2,
            "歴史": 1,
            "権力": 1,
            "主体": 1,
            "言語": 2,
            "イデオロギー": 2,
        },
    },
]

TOPICS = [
    {"title": "神話の役割", "key": "神話"},
    {"title": "親族と交換", "key": "親族"},
    {"title": "主体の位置", "key": "主体"},
    {"title": "権力と規律", "key": "権力"},
    {"title": "歴史の断層", "key": "歴史"},
    {"title": "言語の構造", "key": "言語"},
    {"title": "イデオロギーの働き", "key": "イデオロギー"},
    {"title": "構造と変換", "key": "構造"},
]

OPENERS = [
    "この議題で構造の有効性を示したい。",
    "私はこの論点から出発する。",
    "議論の焦点をここに置こう。",
    "まずこの問題を確定しよう。",
]

RESPONSES = [
    "あなたの指摘は重要だが、前提が違う。",
    "私はその枠組みを拡張したい。",
    "その見取り図には欠落がある。",
    "同意できるが、焦点がずれている。",
]

PUSHES = [
    "結論を急がず構造の層を見よ。",
    "議論は主体の位置から再構成される。",
    "歴史的条件を無視できない。",
    "言説の働きが見落とされている。",
]

CLOSERS = [
    "私はこの点で優位を保つ。",
    "この論点の決定性は動かない。",
    "ここに構造の強さがある。",
    "論理の軸は私にある。",
]

SPECTATOR_REASONS = [
    "議題への適合が弱かった。",
    "具体例よりも抽象に偏った。",
    "他者の主張への応答が遅れた。",
    "構造の提示が一貫しなかった。",
    "争点の再定義に失敗した。",
]

random.seed(42)

AGENT_MAP = {a["id"]: a for a in AGENTS}


def pick_agents():
    a, b = random.sample(AGENTS, 2)
    return a, b


def pick_topic():
    return random.choice(TOPICS)


def score(agent, topic_key):
    base = random.randint(1, 6)
    bias = agent["strengths"].get(topic_key, 1)
    return base + bias


def make_statement(agent, topic_title, phase):
    voice = random.choice(agent["voice"])
    if phase == "open":
        return f"{topic_title}について、{random.choice(OPENERS)} {voice}"
    if phase == "response":
        return f"{random.choice(RESPONSES)} {voice}"
    if phase == "push":
        return f"{random.choice(PUSHES)} {voice}"
    return f"{random.choice(CLOSERS)} {voice}"


def battle(index):
    a, b = pick_agents()
    topic = pick_topic()
    turns = random.randint(12, 30)
    transcript = []

    for t in range(1, turns + 1):
        speaker = a if t % 2 == 1 else b
        if t == 1:
            phase = "open"
        elif t < turns - 2:
            phase = "response"
        elif t < turns:
            phase = "push"
        else:
            phase = "close"
        text = make_statement(speaker, topic["title"], phase)
        transcript.append((t, speaker["name"], text))

    spectators = [x for x in AGENTS if x not in (a, b)]

    score_a = score(a, topic["key"])
    score_b = score(b, topic["key"])
    if score_a == score_b:
        score_b += random.randint(0, 1)

    loser = a if score_a < score_b else b

    votes = []
    for s in spectators:
        reason = random.choice(SPECTATOR_REASONS)
        votes.append((s["name"], loser["name"], reason))

    battle_md = []
    battle_md.append(f"# battle-{index}")
    battle_md.append("")
    battle_md.append("## 参加者")
    battle_md.append(f"- 先手: {a['name']}")
    battle_md.append(f"- 後手: {b['name']}")
    battle_md.append("")
    battle_md.append("## 議題")
    battle_md.append(f"- {topic['title']}")
    battle_md.append("")
    battle_md.append("## ターン制議論")
    for t, name, text in transcript:
        battle_md.append(f"- T{t:02d} {name}: {text}")
    battle_md.append("")
    battle_md.append("## 見物者の判定")
    for s_name, voted_loser, reason in votes:
        battle_md.append(f"- {s_name} は {voted_loser} を敗者と判断した。理由: {reason}")
    battle_md.append("")
    battle_md.append("## 結果")
    battle_md.append(f"- 敗者: {loser['name']}")

    return "\n".join(battle_md), loser["id"]


def main():
    os.makedirs("battles", exist_ok=True)
    losses = {a["id"]: 0 for a in AGENTS}

    for i in range(1, 31):
        md, loser_id = battle(i)
        losses[loser_id] += 1
        path = os.path.join("battles", f"battle-{i}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    sorted_losses = sorted(losses.items(), key=lambda x: (-x[1], x[0]))
    max_loss = sorted_losses[0][1]
    candidates = [k for k, v in losses.items() if v == max_loss]

    if len(candidates) == 1:
        drop_id = candidates[0]
        tiebreak = ""
    else:
        drop_id = random.choice(candidates)
        tiebreak = f"同数だったため、乱択で決定。候補: {', '.join(candidates)}"

    drop_name = AGENT_MAP[drop_id]["name"]

    result_md = []
    result_md.append("# 四天王決定結果")
    result_md.append("")
    result_md.append("## 負け数")
    for agent_id, _ in sorted_losses:
        result_md.append(f"- {AGENT_MAP[agent_id]['name']}: {losses[agent_id]}敗")
    result_md.append("")
    result_md.append("## 脱落")
    result_md.append(f"- 脱落者: {drop_name}")
    if tiebreak:
        result_md.append(f"- 補足: {tiebreak}")

    with open("final.md", "w", encoding="utf-8") as f:
        f.write("\n".join(result_md))

    print("battles written, final.md updated")


if __name__ == "__main__":
    main()
