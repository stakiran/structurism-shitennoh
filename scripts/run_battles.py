# -*- coding: utf-8 -*-
import os
import random
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from agents.althusser import create as create_althusser
from agents.barthes import create as create_barthes
from agents.base import build_client_from_env
from agents.foucault import create as create_foucault
from agents.lacan import create as create_lacan
from agents.levi import create as create_levi

random.seed(42)


def load_agents(client):
    return [
        create_levi(client),
        create_lacan(client),
        create_foucault(client),
        create_althusser(client),
        create_barthes(client),
    ]


def pick_agents(agents):
    return random.sample(agents, 2)


def next_battle_index(battles_dir):
    if not os.path.isdir(battles_dir):
        return 1
    max_idx = 0
    for name in os.listdir(battles_dir):
        m = re.match(r"battle-(\d+)\.md$", name)
        if m:
            max_idx = max(max_idx, int(m.group(1)))
    return max_idx + 1


def parse_topic(first_text):
    m = re.search(r"議題\s*[:：]\s*(.+)", first_text)
    if not m:
        return "構造主義における理論の中核"
    raw = m.group(1).strip()
    first_line = raw.splitlines()[0].strip()
    return first_line if first_line else "構造主義における理論の中核"


def parse_judge(raw_text, a_name, b_name):
    loser = None
    reason = ""

    for line in raw_text.splitlines():
        if line.startswith("敗者:"):
            candidate = line.split(":", 1)[1].strip()
            if candidate in (a_name, b_name):
                loser = candidate
        if line.startswith("理由:"):
            reason = line.split(":", 1)[1].strip()

    if loser is None:
        if a_name in raw_text and b_name not in raw_text:
            loser = a_name
        elif b_name in raw_text and a_name not in raw_text:
            loser = b_name
        else:
            loser = a_name

    if not reason:
        reason = "議論の一貫性と議題適合性の観点で相対的に弱いと判断した。"

    return loser, reason


def transcript_to_text(transcript):
    return "\n".join([f"T{t:02d} {name}: {text}" for t, name, text in transcript])


def battle(index, agents):
    a, b = pick_agents(agents)
    turns = random.randint(12, 30)

    transcript = []

    first_text = a.first_turn()
    topic = parse_topic(first_text)
    transcript.append((1, a.name, first_text.strip()))

    for t in range(2, turns + 1):
        speaker = b if t % 2 == 0 else a
        text = speaker.turn(topic, transcript_to_text(transcript))
        transcript.append((t, speaker.name, text.strip()))

    spectators = [x for x in agents if x not in (a, b)]

    votes = []
    for s in spectators:
        judge_raw = s.judge_loser(topic, transcript_to_text(transcript), a.name, b.name)
        loser_name, reason = parse_judge(judge_raw, a.name, b.name)
        votes.append((s.name, loser_name, reason))

    lose_counts = {a.name: 0, b.name: 0}
    for _, loser_name, _ in votes:
        lose_counts[loser_name] += 1

    if lose_counts[a.name] == lose_counts[b.name]:
        loser = a
    else:
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


def aggregate_losses(agents, battles_dir):
    losses = {a.name: 0 for a in agents}
    for name in os.listdir(battles_dir):
        m = re.match(r"battle-(\d+)\.md$", name)
        if not m:
            continue
        path = os.path.join(battles_dir, name)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        m_loser = re.search(r"-\s*敗者:\s*(.+)", content)
        if not m_loser:
            continue
        loser_name = m_loser.group(1).strip()
        if loser_name in losses:
            losses[loser_name] += 1
    return losses


def write_final(agents, losses):
    sorted_losses = sorted(losses.items(), key=lambda x: (-x[1], x[0]))
    max_loss = sorted_losses[0][1]
    candidates = [k for k, v in losses.items() if v == max_loss]

    if len(candidates) == 1:
        drop_name = candidates[0]
        tiebreak = ""
    else:
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


def main():
    client = build_client_from_env()
    agents = load_agents(client)

    battles_dir = "battles"
    os.makedirs(battles_dir, exist_ok=True)
    index = next_battle_index(battles_dir)
    if index > 30:
        print("already reached 30 battles; no new battle generated")
        losses = aggregate_losses(agents, battles_dir)
        write_final(agents, losses)
        print("final.md updated from existing battles")
        return

    md, _ = battle(index, agents)
    path = os.path.join(battles_dir, f"battle-{index}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)

    losses = aggregate_losses(agents, battles_dir)
    write_final(agents, losses)

    print(f"battle-{index}.md written, final.md updated")


if __name__ == "__main__":
    main()
