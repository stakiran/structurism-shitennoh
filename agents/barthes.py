# -*- coding: utf-8 -*-
from .base import Agent


def create(client):
    return Agent("ロラン・バルト", "profiles/roland-barthes.md", client)
