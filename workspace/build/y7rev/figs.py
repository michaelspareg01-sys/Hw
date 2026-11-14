"""Figures for the Year 7 revision practice pack.

Run: python3 workspace/build/y7rev/figs.py   (writes svg/*.svg)

Every diagram recreates a textbook diagram (ICE-EM Mathematics 7 3rd ed) or draws the data of a
Pack question. Graphs use plots.Graph so that they match the house style.
"""
import os, sys
from math import sin, cos, radians
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from plots import Graph, ACC, INK, FAINT, _txt  # noqa: F401  (house header)

OUT = os.path.join(os.path.dirname(__file__), "svg")
os.makedirs(OUT, exist_ok=True)


def save(name, g):
    with open(os.path.join(OUT, name + ".svg"), "w", encoding="utf-8") as f:
        f.write(g if isinstance(g, str) else g.svg())


if __name__ == "__main__":
    pass
