# -*- coding: utf-8 -*-
from .base import Agent


def create(client):
    return Agent("ジャック・ラカン", "profiles/jacques-lacan.md", client)
