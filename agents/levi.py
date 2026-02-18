# -*- coding: utf-8 -*-
from .base import Agent


def create(client):
    return Agent("クロード・レヴィ＝ストロース", "profiles/claude-levi-strauss.md", client)
