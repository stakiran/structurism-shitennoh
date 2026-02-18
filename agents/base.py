# -*- coding: utf-8 -*-
import os
import re
from collections import Counter

KANJI_RE = re.compile(r"[一-龥]{2,}")


def split_sentences(text):
    parts = re.split(r"(?<=。)|(?<=！)|(?<=？)", text)
    return [p.strip() for p in parts if p.strip()]


def extract_keywords(text, max_words=8):
    words = KANJI_RE.findall(text)
    counts = Counter(words)
    common = [w for w, _ in counts.most_common(max_words * 2)]
    # remove overly generic items if possible
    blacklist = {"構造", "主体", "言語", "歴史", "権力", "社会", "文化", "意味"}
    filtered = [w for w in common if w not in blacklist]
    if len(filtered) < max_words:
        filtered = filtered + [w for w in common if w not in filtered]
    return filtered[:max_words]


class Agent:
    def __init__(self, name, profile_path):
        self.name = name
        self.profile_path = profile_path
        self.profile_text = self._load_profile()
        self.sentences = split_sentences(self.profile_text)
        self.keywords = extract_keywords(self.profile_text)

    def _load_profile(self):
        with open(self.profile_path, "r", encoding="utf-8") as f:
            return f.read()

    def propose_topic(self):
        # pick a topic-like keyword from profile
        if self.keywords:
            return self.keywords[0]
        return "構造"

    def pick_sentence(self, topic=None, used=None):
        used = used or set()
        candidates = []
        for s in self.sentences:
            if s in used:
                continue
            if topic and topic in s:
                candidates.append(s)
        if candidates:
            return candidates[0]
        for s in self.sentences:
            if s not in used:
                return s
        return self.sentences[0] if self.sentences else ""

    def respond(self, topic, context, used_sentences):
        last = context[-1][2] if context else ""
        sentence = self.pick_sentence(topic=topic, used=used_sentences)
        used_sentences.add(sentence)
        if last:
            return f"しかし、{sentence}"
        return sentence

    def vote(self, topic, transcript, debaters):
        # Evaluate who is weaker from this agent's perspective
        # Metrics derived from transcript only: alignment with own keywords, topical focus, rebuttals
        scores = {}
        for debater in debaters:
            statements = [t for t in transcript if t[1] == debater.name]
            text = "".join([t[2] for t in statements])
            alignment = sum(text.count(k) for k in self.keywords)
            topic_focus = text.count(topic)
            rebuttal = text.count("しかし") + text.count("だが") + text.count("一方")
            unique_self_keywords = len({k for k in debater.keywords if k in text})
            scores[debater.name] = alignment + topic_focus + rebuttal + unique_self_keywords
        # loser is lower score; tie-breaker: fewer topic mentions
        a, b = debaters
        if scores[a.name] == scores[b.name]:
            a_topic = sum(t[2].count(topic) for t in transcript if t[1] == a.name)
            b_topic = sum(t[2].count(topic) for t in transcript if t[1] == b.name)
            if a_topic == b_topic:
                # final tie: choose debater who used fewer unique keywords
                a_unique = len({k for k in a.keywords if k in "".join([t[2] for t in transcript if t[1] == a.name])})
                b_unique = len({k for k in b.keywords if k in "".join([t[2] for t in transcript if t[1] == b.name])})
                return a.name if a_unique < b_unique else b.name
            return a.name if a_topic < b_topic else b.name
        return a.name if scores[a.name] < scores[b.name] else b.name
