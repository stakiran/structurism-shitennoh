# -*- coding: utf-8 -*-
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agents.levi import create as create_levi
from agents.lacan import create as create_lacan
from agents.foucault import create as create_foucault
from agents.althusser import create as create_althusser
from agents.barthes import create as create_barthes

OPENERS = [
    "議題をここに置く。",
    "まず焦点を定める。",
    "私の立場から論点を提示する。",
    "この問題から始めよう。",
]

RESPONSES = [
    "あなたの主張を受けて言う。",
    "その前提を押さえたうえで答える。",
    "異議はあるが、議論を進める。",
    "同意しつつ、別の角度を示す。",
]

CLOSERS = [
    "この点は譲れない。",
    "私はここで結論を示す。",
    "この構図が決定的だ。",
    "最後に論点を固定する。",
]

random.seed(42)


def load_agents():
    return [
        create_levi(),
        create_lacan(),
        create_foucault(),
        create_althusser(),
        create_barthes(),
    ]


def pick_agents(agents):
    return random.sample(agents, 2)


def run_turn(agent, topic, context, used_sentences, is_open=False, is_close=False):
    if is_open:
        sentence = agent.respond(topic, context, used_sentences)
        return f"{random.choice(OPENERS)} 議題は『{topic}』だ。 {sentence}"
    if is_close:
        sentence = agent.respond(topic, context, used_sentences)
        return f"{random.choice(CLOSERS)} {sentence}"
    sentence = agent.respond(topic, context, used_sentences)
    return f"{random.choice(RESPONSES)} {sentence}"


def battle(index, agents):
    a, b = pick_agents(agents)
    topic = a.propose_topic()
    turns = random.randint(12, 30)

    transcript = []
    used = {a.name: set(), b.name: set()}

    for t in range(1, turns + 1):
        speaker = a if t % 2 == 1 else b
        if t == 1:
            text = run_turn(speaker, topic, transcript, used[speaker.name], is_open=True)
        elif t == turns:
            text = run_turn(speaker, topic, transcript, used[speaker.name], is_close=True)
        else:
            text = run_turn(speaker, topic, transcript, used[speaker.name])
        transcript.append((t, speaker.name, text))

    spectators = [x for x in agents if x not in (a, b)]

    votes = []
    for s in spectators:
        loser_name = s.vote(topic, transcript, [a, b])
        reason = f"自身の関心語彙との整合と論点集中度を評価した。"
        votes.append((s.name, loser_name, reason))

    lose_counts = {a.name: 0, b.name: 0}
    for _, loser_name, _ in votes:
        lose_counts[loser_name] += 1

    loser = a if lose_counts[a.name] > lose_counts[b.name] else b

    battle_md = []
    battle_md.append(f"# battle-{index}")
    battle_md.append("")
    battle_md.append("## 参加者")
    battle_md.append(f"- 先手: {a.name}")
    battle_md.append(f"- 後手: {b.name}")
    battle_md.append("")
    battle_md.append("## 議題")
    battle_md.append(f"- {topic}")
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
    battle_md.append(f"- 敗者: {loser.name}")

    return "\n".join(battle_md), loser.name


def main():
    agents = load_agents()
    os.makedirs("battles", exist_ok=True)
    losses = {a.name: 0 for a in agents}

    for i in range(1, 31):
        md, loser_name = battle(i, agents)
        losses[loser_name] += 1
        path = os.path.join("battles", f"battle-{i}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(md)

    sorted_losses = sorted(losses.items(), key=lambda x: (-x[1], x[0]))
    max_loss = sorted_losses[0][1]
    candidates = [k for k, v in losses.items() if v == max_loss]

    if len(candidates) == 1:
        drop_name = candidates[0]
        tiebreak = ""
    else:
        # tie-breaker based on alphabetical (deterministic)
        drop_name = sorted(candidates)[0]
        tiebreak = f"同数だったため、五十音順で決定。候補: {', '.join(sorted(candidates))}"

    result_md = []
    result_md.append("# 四天王決定結果")
    result_md.append("")
    result_md.append("## 負け数")
    for name, _ in sorted_losses:
        result_md.append(f"- {name}: {losses[name]}敗")
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
