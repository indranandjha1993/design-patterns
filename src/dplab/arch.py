"""Helpers and labs for the architecture track: component diagrams, dependency rules,
a network latency simulator, an event bus with lag, and an architecture picker."""
import math
import random
import ipywidgets as w
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
from IPython.display import display, HTML
from .common import is_static, caption, display_static, show_in, close_if_inline


# ---------------------------------------------------------------------------
# Component diagrams and dependency rules
# ---------------------------------------------------------------------------
def component_diagram(components, edges=(), groups=None, layout=None, bad_edges=(), title="", xgap=2.6, ygap=1.1):
    # components: list of names. edges: (src, dst[, label]). groups: {group name: [members]} drawn as dashed boxes.
    # bad_edges: set of (src, dst) drawn in red (rule violations).
    components = list(components)
    if layout is None:
        layout = {}
        if groups:
            col = 0
            placed = set()
            for gname, members in groups.items():
                for row, m in enumerate(members):
                    layout[m] = (col, row)
                    placed.add(m)
                col += 1
            for row, m in enumerate(c for c in components if c not in placed):
                layout[m] = (col, row)
        else:
            cols = max(1, math.ceil(math.sqrt(len(components))))
            for i, c in enumerate(components):
                layout[c] = (i % cols, i // cols)
    boxes = {c: (layout[c][0] * xgap, -layout[c][1] * ygap, 2.0, 0.7) for c in components}
    xs = [b[0] for b in boxes.values()]
    ys = [b[1] for b in boxes.values()]
    fig, ax = plt.subplots(figsize=(max(4, (max(xs) - min(xs)) * 1.3 + 3.2), max(2.4, (max(ys) - min(ys)) * 1.3 + 2.2)))
    if groups:
        for gname, members in groups.items():
            gx = [boxes[m][0] for m in members]
            gy = [boxes[m][1] for m in members]
            x0, x1 = min(gx) - 1.2, max(gx) + 1.2
            y0, y1 = min(gy) - 0.55, max(gy) + 0.55
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0 + 0.35, facecolor="#f7f7f7", edgecolor="#777", ls="--", lw=1, zorder=0))
            ax.text(x0 + 0.1, y1 + 0.28, gname, fontsize=8, color="#555", ha="left", va="center")
    for c, (x, y, bw, bh) in boxes.items():
        ax.add_patch(Rectangle((x - bw / 2, y - bh / 2), bw, bh, facecolor="#f4f7fb", edgecolor="#333", lw=1.2, zorder=2))
        ax.text(x, y, c, ha="center", va="center", fontsize=8, fontweight="bold", zorder=3)
    for e in edges:
        src, dst = e[:2]
        label = e[2] if len(e) > 2 else None
        (x1, y1, w1, h1), (x2, y2, w2, h2) = boxes[src], boxes[dst]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        # shorten so the arrow starts and ends at the box edges
        sx = min(w1 / 2 / max(abs(dx / L), 1e-9), h1 / 2 / max(abs(dy / L), 1e-9)) if L else 0
        ex = min(w2 / 2 / max(abs(dx / L), 1e-9), h2 / 2 / max(abs(dy / L), 1e-9)) if L else 0
        p1 = (x1 + dx / L * sx, y1 + dy / L * sx)
        p2 = (x2 - dx / L * ex, y2 - dy / L * ex)
        bad = (src, dst) in set(bad_edges)
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="->", mutation_scale=13, edgecolor="tab:red" if bad else "#333",
                                     facecolor="tab:red" if bad else "#333", lw=1.6 if bad else 1.1, zorder=1,
                                     connectionstyle="arc3,rad=0.1"))
        if label:
            ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 0.12, label, fontsize=7, ha="center", color="#555",
                    bbox=dict(fc="white", ec="none", pad=1), zorder=4)
    ax.set_xlim(min(xs) - 1.6, max(xs) + 1.6)
    ax.set_ylim(min(ys) - 0.9, max(ys) + 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=10)
    return close_if_inline(fig)


def check_dependencies(deps, allowed):
    # deps: {module: set of modules it imports}. allowed: {module: set of modules it may import}.
    # Returns the list of (module, imported) pairs that break the rules.
    return [(m, d) for m, ds in deps.items() for d in sorted(ds) if d != m and d not in allowed.get(m, set())]


# ---------------------------------------------------------------------------
# Network latency and availability simulator
# ---------------------------------------------------------------------------
def simulate_requests(n_services, mean_ms, fail_pct, retries=0, parallel=False, samples=3000, seed=1):
    # Each request touches n_services. A call fails with probability fail_pct/100 and is retried up to `retries` times.
    # Latency per attempt is lognormal around mean_ms. Sequential: latencies add; parallel: the slowest wins.
    rng = random.Random(seed)
    p = fail_pct / 100
    sigma = 0.5
    mu = math.log(mean_ms) - sigma ** 2 / 2
    latencies, successes = [], 0
    for _ in range(samples):
        ok = True
        per_call = []
        for _s in range(n_services):
            total, success = 0.0, False
            for _attempt in range(retries + 1):
                total += rng.lognormvariate(mu, sigma)
                if rng.random() >= p:
                    success = True
                    break
            per_call.append(total)
            if not success:
                ok = False
        latencies.append(max(per_call) if parallel else sum(per_call))
        successes += ok
    latencies.sort()
    q = lambda f: latencies[min(len(latencies) - 1, int(f * len(latencies)))]
    return {"success_rate": successes / samples, "p50": q(0.5), "p95": q(0.95), "p99": q(0.99), "latencies": latencies,
            "theory_success": (1 - p ** (retries + 1)) ** n_services}


class LatencyLab:
    def __init__(self):
        self._build_ui()
        self._render()

    def figure(self):
        r = simulate_requests(self.n.value, self.mean.value, self.fail.value, self.retries.value, self.mode.value == "parallel fan-out")
        fig, ax = plt.subplots(figsize=(8, 3.3))
        ax.hist(r["latencies"], bins=60, color="tab:blue", alpha=0.8)
        for name, v, c in (("p50", r["p50"], "tab:green"), ("p95", r["p95"], "tab:orange"), ("p99", r["p99"], "tab:red")):
            ax.axvline(v, color=c, ls="--", lw=1.2, label=f"{name} = {v:.0f} ms")
        ax.set_xlabel("end-to-end latency (ms)")
        ax.set_ylabel("requests")
        ax.set_title(f"{self.n.value} services, {self.mean.value} ms mean each, {self.fail.value}% failure per call, {self.retries.value} retries, {self.mode.value}", fontsize=9)
        ax.legend(fontsize=8)
        fig.tight_layout()
        html = (f"<span style='font-family:monospace; font-size:12px'>success rate {r['success_rate']:.1%} "
                f"(theory {r['theory_success']:.1%} = (1 - p^(retries+1))^services) &nbsp;|&nbsp; "
                f"p50 {r['p50']:.0f} ms, p95 {r['p95']:.0f} ms, p99 {r['p99']:.0f} ms</span>")
        return close_if_inline(fig), html

    def _build_ui(self):
        self.n = w.IntSlider(value=5, min=1, max=12, step=1, description="services", continuous_update=False, layout=w.Layout(width="300px"))
        self.mean = w.IntSlider(value=20, min=2, max=200, step=2, description="mean ms", continuous_update=False, layout=w.Layout(width="300px"))
        self.fail = w.FloatSlider(value=1.0, min=0, max=10, step=0.5, description="fail %", continuous_update=False, readout_format=".1f", layout=w.Layout(width="300px"))
        self.retries = w.IntSlider(value=0, min=0, max=3, step=1, description="retries", continuous_update=False, layout=w.Layout(width="300px"))
        self.mode = w.Dropdown(options=["sequential chain", "parallel fan-out"], description="calls", layout=w.Layout(width="260px"))
        for widget in (self.n, self.mean, self.fail, self.retries, self.mode):
            widget.observe(lambda ch: self._render(), names="value")
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Latency and Availability Lab.</b> One user request touches several services over the network. See what the chain does to tail latency and success rate.")
        self.ui = w.VBox([header, w.HBox([self.n, self.mean]), w.HBox([self.fail, self.retries]), self.mode, self.out, self.info])

    def _render(self):
        fig, html = self.figure()
        show_in(self.out, fig)
        self.info.value = html


def latency_lab(static=None):
    """Open the Latency and Availability Lab."""
    lab = LatencyLab()
    if is_static(static):
        caption("Latency and Availability Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        fig, html = lab.figure()
        display_static(fig)
        display(HTML(html))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Event bus with lag, and a CQRS read model
# ---------------------------------------------------------------------------
class EventBus:
    # Publish appends to a queue; deliver(k) hands at most k events to subscribers. The gap is the consumer lag.
    def __init__(self):
        self.subscribers = {}
        self.pending = []
        self.delivered = []

    def subscribe(self, topic, handler):
        self.subscribers.setdefault(topic, []).append(handler)

    def publish(self, topic, payload):
        self.pending.append((topic, payload))

    def deliver(self, k):
        for _ in range(min(k, len(self.pending))):
            topic, payload = self.pending.pop(0)
            for handler in self.subscribers.get(topic, []):
                handler(payload)
            self.delivered.append((topic, payload))


class OrderWriteModel:
    def __init__(self, bus):
        self.bus = bus
        self.orders = {}
        self.next_id = 1

    def place(self, item, amount):
        oid = self.next_id
        self.next_id += 1
        self.orders[oid] = {"item": item, "amount": amount, "status": "placed"}
        self.bus.publish("OrderPlaced", {"id": oid, "item": item, "amount": amount})
        return oid

    def pay(self, oid):
        if oid in self.orders and self.orders[oid]["status"] == "placed":
            self.orders[oid]["status"] = "paid"
            self.bus.publish("OrderPaid", {"id": oid, "amount": self.orders[oid]["amount"]})

    def ship(self, oid):
        if oid in self.orders and self.orders[oid]["status"] == "paid":
            self.orders[oid]["status"] = "shipped"
            self.bus.publish("OrderShipped", {"id": oid})


class DashboardReadModel:
    # Built only from events: it never reads the write model.
    def __init__(self, bus):
        self.placed = self.paid = self.shipped = 0
        self.revenue = 0.0
        bus.subscribe("OrderPlaced", self.on_placed)
        bus.subscribe("OrderPaid", self.on_paid)
        bus.subscribe("OrderShipped", self.on_shipped)

    def on_placed(self, e):
        self.placed += 1

    def on_paid(self, e):
        self.paid += 1
        self.revenue += e["amount"]

    def on_shipped(self, e):
        self.shipped += 1


class EventLab:
    def __init__(self):
        self.bus = EventBus()
        self.writes = OrderWriteModel(self.bus)
        self.reads = DashboardReadModel(self.bus)
        self._build_ui()
        self._render()

    def truth(self):
        o = self.writes.orders.values()
        return {"placed": len(o), "paid": sum(1 for x in o if x["status"] in ("paid", "shipped")),
                "shipped": sum(1 for x in o if x["status"] == "shipped"),
                "revenue": sum(x["amount"] for x in o if x["status"] in ("paid", "shipped"))}

    def figure(self):
        t, r = self.truth(), self.reads
        labels = ["placed", "paid", "shipped"]
        fig, ax = plt.subplots(figsize=(7, 3))
        xs = range(len(labels))
        ax.bar([x - 0.18 for x in xs], [t[k] for k in labels], width=0.36, label="write model (truth)", color="tab:blue")
        ax.bar([x + 0.18 for x in xs], [r.placed, r.paid, r.shipped], width=0.36, label="dashboard read model", color="tab:orange")
        ax.set_xticks(list(xs))
        ax.set_xticklabels(labels)
        ax.set_title(f"pending events: {len(self.bus.pending)}   (the read model catches up as events are delivered)", fontsize=9)
        ax.legend(fontsize=8)
        fig.tight_layout()
        return close_if_inline(fig)

    def html(self):
        t, r = self.truth(), self.reads
        pending = ", ".join(f"{topic}#{p['id']}" for topic, p in self.bus.pending[:8]) + (" ..." if len(self.bus.pending) > 8 else "")
        return (f"<span style='font-family:monospace; font-size:12px'>write model: {t} &nbsp;|&nbsp; "
                f"read model: placed {r.placed}, paid {r.paid}, shipped {r.shipped}, revenue {r.revenue:.0f}<br>"
                f"pending: [{pending or 'none'}]</span>")

    def _build_ui(self):
        place = w.Button(description="Place order", button_style="primary", layout=w.Layout(width="110px"))
        pay = w.Button(description="Pay oldest unpaid", layout=w.Layout(width="140px"))
        ship = w.Button(description="Ship oldest paid", layout=w.Layout(width="130px"))
        self.speed = w.IntSlider(value=2, min=1, max=10, step=1, description="deliver per tick", continuous_update=False, layout=w.Layout(width="300px"))
        tick = w.Button(description="Tick (deliver)", button_style="success", layout=w.Layout(width="120px"))
        place.on_click(lambda _b: (self.writes.place(random.choice(["book", "lamp", "chair"]), random.choice([10, 25, 40])), self._render()))
        pay.on_click(lambda _b: (self._first("placed", self.writes.pay), self._render()))
        ship.on_click(lambda _b: (self._first("paid", self.writes.ship), self._render()))
        tick.on_click(lambda _b: (self.bus.deliver(self.speed.value), self._render()))
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Event Lab.</b> Writes go to the order model and publish events. The dashboard is a separate read model built only from events, so it lags until you tick.")
        self.ui = w.VBox([header, w.HBox([place, pay, ship]), w.HBox([self.speed, tick]), self.out, self.info])

    def _first(self, status, action):
        for oid, o in self.writes.orders.items():
            if o["status"] == status:
                action(oid)
                return

    def _render(self):
        show_in(self.out, self.figure())
        self.info.value = self.html()


def event_lab(static=None):
    """Open the Event Lab (pub/sub with consumer lag and a CQRS read model)."""
    lab = EventLab()
    if is_static(static):
        caption("Event Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        random.seed(2)
        for _ in range(4):
            lab.writes.place("book", 25)
        lab.writes.pay(1); lab.writes.pay(2); lab.writes.ship(1)
        lab.bus.deliver(3)
        display_static(lab.figure())
        display(HTML(lab.html()))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Architecture picker
# ---------------------------------------------------------------------------
QUESTIONS_ARCH = {
    "team": ("team size", ["1 to 5", "6 to 20", "more than 20"]),
    "domain": ("how well is the domain understood?", ["new and unclear", "reasonably clear", "stable and well known"]),
    "deploy": ("do parts need independent deployment?", ["no", "sometimes", "critical"]),
    "scale": ("scaling needs", ["uniform, modest", "a few hot spots", "very different per part"]),
    "ops": ("operations maturity (CI/CD, monitoring, on-call)", ["basic", "solid", "advanced"]),
}


def score_architectures(answers):
    # answers: {key: index}. Returns [(architecture, score, reasons)] sorted best first. Heuristic, not gospel.
    team, domain, deploy, scale, ops = (answers[k] for k in ("team", "domain", "deploy", "scale", "ops"))
    scores = {"monolith": 0, "modular monolith": 0, "microservices": 0, "event-driven services": 0}
    reasons = {k: [] for k in scores}
    if team == 0:
        scores["monolith"] += 3; reasons["monolith"].append("small team: one deployable is cheapest to run")
        scores["modular monolith"] += 2
        scores["microservices"] -= 2; reasons["microservices"].append("small team: too much operational overhead")
    elif team == 1:
        scores["modular monolith"] += 3; reasons["modular monolith"].append("mid-size team: boundaries matter, the network does not yet")
        scores["microservices"] += 1
    else:
        scores["microservices"] += 3; reasons["microservices"].append("many teams: independent ownership pays off")
        scores["event-driven services"] += 2
        scores["monolith"] -= 2; reasons["monolith"].append("large org: one codebase becomes a bottleneck")
    if domain == 0:
        scores["modular monolith"] += 2; reasons["modular monolith"].append("unclear domain: boundaries will move, keep them cheap to move")
        scores["microservices"] -= 3; reasons["microservices"].append("unclear domain: wrong service boundaries are very expensive")
    elif domain == 2:
        scores["microservices"] += 1
    if deploy == 2:
        scores["microservices"] += 3; reasons["microservices"].append("independent deployment is the core promise of services")
        scores["event-driven services"] += 2
        scores["monolith"] -= 2
    elif deploy == 1:
        scores["modular monolith"] += 1
    if scale == 2:
        scores["microservices"] += 2; reasons["microservices"].append("parts scale differently: scale them separately")
        scores["event-driven services"] += 2; reasons["event-driven services"].append("bursty, uneven load suits queues and consumers")
    elif scale == 1:
        scores["modular monolith"] += 1; reasons["modular monolith"].append("a few hot spots can be scaled by running more copies or extracting one module later")
    if ops == 0:
        scores["microservices"] -= 3; reasons["microservices"].append("basic ops: distributed systems need monitoring, tracing and automated deploys first")
        scores["event-driven services"] -= 2
        scores["monolith"] += 1
    elif ops == 2:
        scores["microservices"] += 1
        scores["event-driven services"] += 1
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    return [(name, score, reasons[name]) for name, score in ranked]


class ArchitecturePicker:
    def __init__(self):
        self._build_ui()
        self._render()

    def answers(self):
        return {k: dd.index for k, dd in self.dds.items()}

    def html(self, answers=None):
        ranked = score_architectures(answers or self.answers())
        rows = "".join(f"<tr><td><b>{name}</b></td><td>{score:+d}</td><td>{'; '.join(reasons) or '-'}</td></tr>" for name, score, reasons in ranked)
        return ("<table style='font-size:12px; border-collapse:collapse'><tr><th style='text-align:left'>architecture</th><th>score</th><th style='text-align:left'>why</th></tr>"
                + rows + "</table><div style='font-size:11px; color:#666; margin-top:4px'>A heuristic to start the conversation, not a verdict. Most teams should begin with the second row and earn the first.</div>")

    def _build_ui(self):
        self.dds = {}
        rows = []
        for key, (label, options) in QUESTIONS_ARCH.items():
            dd = w.Dropdown(options=options, description=label, layout=w.Layout(width="520px"), style={"description_width": "300px"})
            dd.observe(lambda ch: self._render(), names="value")
            self.dds[key] = dd
            rows.append(dd)
        self.info = w.HTML()
        header = w.HTML("<b>Architecture Picker.</b> Answer five questions about your situation.")
        self.ui = w.VBox([header] + rows + [self.info])

    def _render(self):
        self.info.value = self.html()


def architecture_picker(static=None):
    """Open the Architecture Picker."""
    lab = ArchitecturePicker()
    if is_static(static):
        caption("Architecture Picker (static preview). Run this cell in JupyterLab for the interactive version.")
        display(HTML(lab.html({"team": 1, "domain": 0, "deploy": 1, "scale": 1, "ops": 1})))
        return None
    display(lab.ui)
    return None
