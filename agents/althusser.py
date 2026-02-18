# -*- coding: utf-8 -*-
from .base import Agent


def create(client):
    return Agent("ルイ・アルチュセール", "profiles/louis-althusser.md", client)
