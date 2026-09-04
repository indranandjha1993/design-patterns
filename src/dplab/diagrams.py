"""Diagram drawers: class diagrams, sequence diagrams, state diagrams, trees, chains, stacks, nested boxes."""
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
from .common import close_if_inline

CHAR_W = 0.085
LINE_H = 0.19


def _box_size(name, members):
    longest = max([len(name) + 2] + [len(m) for m in members] + [10])
    w = longest * CHAR_W + 0.35
    h = 0.34 + (LINE_H * len(members) + 0.12 if members else 0)
    return w, h


def _auto_layout(names, relations):
    parents = {}
    for rel in relations:
        src, dst, kind = rel[:3]
        if kind in ("inherits", "implements"):
            parents.setdefault(src, []).append(dst)

    def level(n, seen=()):
        if n not in parents or n in seen:
            return 0
        return 1 + max(level(p, seen + (n,)) for p in parents[n])

    rows = {}
    for n in names:
        rows.setdefault(level(n), []).append(n)
    layout = {}
    for lv, row in rows.items():
        for i, n in enumerate(row):
            layout[n] = (i - (len(row) - 1) / 2, lv)
    return layout


def _anchor(box, toward):
    x, y, w, h = box
    dx, dy = toward[0] - x, toward[1] - y
    if dx == 0 and dy == 0:
        return x, y
    if abs(dx) * h >= abs(dy) * w:
        sx = w / 2 if dx > 0 else -w / 2
        return x + sx, y + dy * (sx / dx)
    sy = h / 2 if dy > 0 else -h / 2
    return x + dx * (sy / dy), y + sy


def class_diagram(classes, relations=(), abstract=(), layout=None, title="", xgap=2.7, ygap=1.6, figsize=None):
    # classes: {name: [members]}. relations: (src, dst, kind[, label]) with kind in
    # inherits (solid, hollow triangle), implements (dashed, hollow triangle), has (diamond at src), uses (dashed arrow), refers (solid arrow).
    names = list(classes)
    layout = layout or _auto_layout(names, relations)
    boxes = {}
    for n in names:
        gx, gy = layout[n]
        w, h = _box_size(n, classes[n])
        boxes[n] = (gx * xgap, -gy * ygap, w, h)
    xs = [b[0] for b in boxes.values()]
    ys = [b[1] for b in boxes.values()]
    ws = max(b[2] for b in boxes.values())
    hs = max(b[3] for b in boxes.values())
    width = (max(xs) - min(xs)) + ws + 1
    height = (max(ys) - min(ys)) + hs + 1
    fig, ax = plt.subplots(figsize=figsize or (max(4, width * 1.5), max(2.4, height * 1.5)))
    for n, (x, y, w, h) in boxes.items():
        ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, facecolor="#f4f7fb", edgecolor="#333", lw=1.2, zorder=2))
        members = classes[n]
        top = y + h / 2
        ax.text(x, top - 0.17, n, ha="center", va="center", fontsize=9, fontweight="bold",
                style="italic" if n in abstract else "normal", zorder=3)
        if members:
            ax.plot([x - w / 2, x + w / 2], [top - 0.34, top - 0.34], color="#333", lw=1, zorder=3)
            for i, m in enumerate(members):
                ax.text(x - w / 2 + 0.08, top - 0.34 - 0.06 - LINE_H * (i + 0.5), m, ha="left", va="center",
                        fontsize=8, family="monospace", zorder=3)
    for rel in relations:
        src, dst, kind = rel[:3]
        label = rel[3] if len(rel) > 3 else None
        b1, b2 = boxes[src], boxes[dst]
        p1 = _anchor(b1, (b2[0], b2[1]))
        p2 = _anchor(b2, (b1[0], b1[1]))
        ls = "--" if kind in ("implements", "uses") else "-"
        if kind in ("inherits", "implements"):
            arrow = FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=18, linestyle=ls,
                                    edgecolor="#333", facecolor="white", lw=1.2, zorder=1)
        else:
            arrow = FancyArrowPatch(p1, p2, arrowstyle="->", mutation_scale=14, linestyle=ls,
                                    edgecolor="#333", facecolor="#333", lw=1.2, zorder=1)
            if kind == "has":
                ax.plot([p1[0]], [p1[1]], marker="D", markersize=7, color="#333", zorder=3)
        ax.add_patch(arrow)
        if label:
            ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 0.1, label, fontsize=7, ha="center", color="#555",
                    bbox=dict(fc="white", ec="none", pad=1), zorder=4)
    ax.set_xlim(min(xs) - ws / 2 - 0.5, max(xs) + ws / 2 + 0.5)
    ax.set_ylim(min(ys) - hs / 2 - 0.5, max(ys) + hs / 2 + 0.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def sequence_diagram(participants, messages, title="", figsize=None):
    # messages: (src, dst, label) or (src, dst, label, kind) with kind 'call' or 'return'.
    xs = {p: i * 2.4 for i, p in enumerate(participants)}
    n = len(messages)
    height = 0.9 + 0.5 * (n + 1)
    fig, ax = plt.subplots(figsize=figsize or (max(4, 2.4 * len(participants) + 0.6), max(2.4, 0.42 * (n + 3))))
    for p, x in xs.items():
        ax.add_patch(Rectangle((x - 0.95, -0.5), 1.9, 0.5, facecolor="#f4f7fb", edgecolor="#333", zorder=2))
        ax.text(x, -0.25, p, ha="center", va="center", fontsize=8, fontweight="bold", zorder=3)
        ax.plot([x, x], [-0.5, -height], ls="--", color="#999", lw=0.9, zorder=1)
    for k, msg in enumerate(messages):
        src, dst, label = msg[:3]
        kind = msg[3] if len(msg) > 3 else "call"
        y = -0.9 - 0.5 * k
        x1, x2 = xs[src], xs[dst]
        style = "--" if kind == "return" else "-"
        if src == dst:
            ax.plot([x1, x1 + 0.55, x1 + 0.55], [y, y, y - 0.22], color="#333", lw=1, ls=style)
            ax.annotate("", xy=(x1 + 0.04, y - 0.22), xytext=(x1 + 0.55, y - 0.22),
                        arrowprops=dict(arrowstyle="->", color="#333", lw=1, linestyle=style))
            ax.text(x1 + 0.65, y - 0.05, label, fontsize=7, ha="left", va="center", family="monospace")
        else:
            ax.annotate("", xy=(x2, y), xytext=(x1, y),
                        arrowprops=dict(arrowstyle="->", color="#333", lw=1, linestyle=style))
            ax.text((x1 + x2) / 2, y + 0.08, label, fontsize=7, ha="center", va="bottom", family="monospace")
    ax.set_xlim(-1.3, max(xs.values()) + 1.3)
    ax.set_ylim(-height - 0.2, 0.2)
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def state_diagram(states, transitions, current=None, title="", size=5.4):
    # transitions: (src, event, dst)
    n = len(states)
    r = 2.2 if n > 2 else 1.6
    pos = {s: (math.cos(2 * math.pi * i / n + math.pi / 2) * r, math.sin(2 * math.pi * i / n + math.pi / 2) * r)
           for i, s in enumerate(states)}
    fig, ax = plt.subplots(figsize=(size, size))
    for src, event, dst in transitions:
        (x1, y1), (x2, y2) = pos[src], pos[dst]
        if src == dst:
            ax.annotate("", xy=(x1 + 0.3, y1 + 0.5), xytext=(x1 - 0.3, y1 + 0.5),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-1.8", color="#333"))
            ax.text(x1, y1 + 1.15, event, ha="center", fontsize=7, color="#555")
        else:
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.25", color="#333", shrinkA=28, shrinkB=28))
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            ax.text(mx + dy / L * 0.42, my - dx / L * 0.42, event, ha="center", va="center", fontsize=7, color="#555",
                    bbox=dict(fc="white", ec="none", pad=1))
    for s, (x, y) in pos.items():
        ax.add_patch(Circle((x, y), 0.6, facecolor="tab:orange" if s == current else "#f4f7fb", edgecolor="#333",
                            lw=1.6 if s == current else 1, zorder=3))
        ax.text(x, y, s, ha="center", va="center", fontsize=8, zorder=4, fontweight="bold" if s == current else "normal")
    lim = r + 1.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def tree_diagram(root, children, label, title="", highlight=(), figsize=None):
    # General tree (any number of children). Nodes are compared by identity.
    pos, order = {}, []

    def place(node, depth, counter):
        kids = list(children(node))
        order.append(node)
        if not kids:
            pos[id(node)] = (counter[0], -depth)
            counter[0] += 1
        else:
            for k in kids:
                place(k, depth + 1, counter)
            xs = [pos[id(k)][0] for k in kids]
            pos[id(node)] = (sum(xs) / len(xs), -depth)

    place(root, 0, [0])
    leaves = max(1, sum(1 for n in order if not list(children(n))))
    depth = max(-y for _, y in pos.values()) + 1
    fig, ax = plt.subplots(figsize=figsize or (max(3.5, 1.2 * leaves + 1), max(2.2, 0.9 * depth)))
    for node in order:
        x, y = pos[id(node)]
        for k in children(node):
            kx, ky = pos[id(k)]
            ax.plot([x, kx], [y, ky], color="#888", lw=1.1, zorder=1)
    for node in order:
        x, y = pos[id(node)]
        hl = any(node is h for h in highlight)
        text = label(node)
        w = max(0.7, len(text) * 0.13 + 0.3)
        ax.add_patch(Rectangle((x - w / 2, y - 0.22), w, 0.44, facecolor="tab:orange" if hl else "#f4f7fb",
                               edgecolor="#333", zorder=2))
        ax.text(x, y, text, ha="center", va="center", fontsize=8, family="monospace", zorder=3)
    ax.set_xlim(-0.8, leaves - 0.2)
    ax.set_ylim(-depth + 0.5, 0.6)
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def chain_diagram(handlers, handled_by=None, passed=(), title=""):
    n = len(handlers)
    fig, ax = plt.subplots(figsize=(max(4, 2.2 * n), 1.9))
    for i, h in enumerate(handlers):
        x = i * 2.2
        if h == handled_by:
            fc, txt = "#c8f0c8", "handles"
        elif h in passed:
            fc, txt = "#eeeeee", "passes on"
        else:
            fc, txt = "#f4f7fb", ""
        ax.add_patch(Rectangle((x - 0.8, -0.35), 1.6, 0.7, facecolor=fc, edgecolor="#333", zorder=2))
        ax.text(x, 0.05, h, ha="center", va="center", fontsize=8, fontweight="bold", zorder=3)
        ax.text(x, -0.2, txt, ha="center", va="center", fontsize=7, color="#555", zorder=3)
        if i < n - 1:
            ax.annotate("", xy=(x + 1.4, 0), xytext=(x + 0.8, 0), arrowprops=dict(arrowstyle="->", color="#333"))
    ax.set_xlim(-1.1, 2.2 * (n - 1) + 1.1)
    ax.set_ylim(-0.7, 0.7)
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def stacks_diagram(stacks, title=""):
    # stacks: {name: [labels bottom to top]}
    names = list(stacks)
    tallest = max([len(v) for v in stacks.values()] + [1])
    fig, ax = plt.subplots(figsize=(2.6 * len(names) + 1, 0.5 * tallest + 1.2))
    for i, name in enumerate(names):
        x = i * 2.6
        ax.text(x, -0.55, name, ha="center", va="center", fontsize=9, fontweight="bold")
        ax.plot([x - 1, x + 1], [-0.3, -0.3], color="#333", lw=1.5)
        items = stacks[name]
        for j, lab in enumerate(items):
            top = j == len(items) - 1
            ax.add_patch(Rectangle((x - 0.95, j * 0.5 - 0.25), 1.9, 0.45, facecolor="#ffe9c6" if top else "#f4f7fb", edgecolor="#333"))
            ax.text(x, j * 0.5 - 0.03, lab, ha="center", va="center", fontsize=7, family="monospace")
        if not items:
            ax.text(x, 0, "(empty)", ha="center", va="center", fontsize=7, color="#999")
    ax.set_xlim(-1.3, 2.6 * (len(names) - 1) + 1.3)
    ax.set_ylim(-0.9, 0.5 * tallest + 0.2)
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def nested_boxes(layers, core, title=""):
    # layers: outermost wrapper first.
    n = len(layers)
    fig, ax = plt.subplots(figsize=(max(4, 1.0 * n + 3.5), max(2.2, 0.6 * n + 1.6)))
    for i, name in enumerate(layers):
        w = 3 + (n - i) * 1.0
        h = 1 + (n - i) * 0.6
        ax.add_patch(Rectangle((-w / 2, -h / 2), w, h, facecolor=plt.cm.Blues(0.12 + 0.1 * i), edgecolor="#333", zorder=i))
        ax.text(-w / 2 + 0.1, h / 2 - 0.2, name, fontsize=8, ha="left", va="center", zorder=n + 2)
    ax.add_patch(Rectangle((-1.4, -0.4), 2.8, 0.8, facecolor="#ffe9c6", edgecolor="#333", zorder=n + 1))
    ax.text(0, 0, core, ha="center", va="center", fontsize=8, zorder=n + 3)
    lw, lh = 3 + n * 1.0, 1 + n * 0.6
    ax.set_xlim(-lw / 2 - 0.3, lw / 2 + 0.3)
    ax.set_ylim(-lh / 2 - 0.3, lh / 2 + 0.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)
