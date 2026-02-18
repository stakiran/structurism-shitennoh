# -*- coding: utf-8 -*-
from .base import Agent


def create(client):
    return Agent("ミシェル・フーコー", "profiles/michel-foucault.md", client)
