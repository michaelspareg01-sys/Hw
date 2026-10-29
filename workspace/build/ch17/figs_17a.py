"""Figures for Lesson 17A (kept apart from figs.py, which Task 1 owns).

Run: python3 workspace/build/ch17/figs_17a.py   (writes svg/c17a_*.svg and svg/a17a_*.svg)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import Fig, save, _txt, ACC, INK  # noqa: E402


def tree(name, stages, s_lab, f_lab, p_s, p_f, num_s, num_f, den, stage_word, labels=None, row=23,
         step=78, fs=1.0):
    """Binary probability tree with `stages` identical stages. Upper branch = success s_lab
    (probability p_s = num_s/den_1), lower branch = failure f_lab. Leaves get the outcome
    (in order) and its probability num/den. Branch probabilities are printed on the first
    `labels` stages (default: all)."""
    labels = stages if labels is None else labels
    leaves = 2 ** stages
    top = 34
    xs = [34 + step * s for s in range(stages + 1)]
    xo = xs[-1] + 60 * fs
    xp = xo + 64 * fs
    w, h = xp + 38 * fs, top + leaves * row + 6
    f = Fig(w, h)
    f.text(xs[0], 20, "Start", size=10.5 * fs, color="faint")
    for s in range(1, stages + 1):
        f.text(xs[s], 20, ["1st", "2nd", "3rd", "4th"][s - 1] + " " + stage_word, size=10.5 * fs, color="faint")
    f.text(xo, 20, "outcome", size=10.5 * fs, color="faint").text(xp, 20, "probability", size=10.5 * fs, color="faint")

    def ys(stage, i):
        span = leaves >> stage                   # leaves under this node
        return top + (i * span + span / 2) * row

    for stage in range(1, stages + 1):
        for i in range(2 ** stage):
            x0 = xs[stage - 1] + (10 if stage > 1 else 4)
            y0 = ys(stage - 1, i // 2)
            x1, y1 = xs[stage] - 10, ys(stage, i)
            f.line(x0, y0, x1, y1, width=1.1)
            succ = i % 2 == 0
            f.text(xs[stage], y1, s_lab if succ else f_lab, size=12 * fs, italic=True)
            if stage <= labels:
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2
                f.raw(_txt(mx - 6, my + (-12 if succ else 12) * fs, p_s if succ else p_f, size=10 * fs, color=ACC["blue"]))
    for k in range(leaves):
        out = "".join(s_lab if c == "0" else f_lab for c in format(k, f"0{stages}b"))
        nf = out.count(f_lab)
        y = ys(stages, k)
        f.text(xo, y, out, size=11.5 * fs, italic=True)
        # plain 'a/b' on one line (the _txt helper would stack it)
        f.raw(f'<text x="{xp:.1f}" y="{y + 4 * fs:.1f}" text-anchor="middle" font-size="{11 * fs:.1f}" '
              f'fill="{INK}">{num_s ** (stages - nf) * num_f ** nf}/{den}</text>')
    save(name, f)


if __name__ == "__main__":
    # lesson, Concept 2 worked example: a die thrown four times, S = six (textbook labels stages 1-3)
    tree("c17a_tree", 4, "S", "F", "1/6", "5/6", 1, 5, 1296, "throw", labels=3)
    # answers C2: spinner red with probability 1/3, three spins; card a heart, three draws
    tree("a17a_spin", 3, "R", "N", "1/3", "2/3", 1, 2, 27, "spin", labels=2, row=28, step=72, fs=1.25)
    tree("a17a_heart", 3, "H", "N", "1/4", "3/4", 1, 3, 64, "draw", labels=2, row=28, step=72, fs=1.25)
