"""Interactive labs for the Gang of Four track."""
import json
import random
import tracemalloc
import ipywidgets as w
import matplotlib.pyplot as plt
from IPython.display import display, HTML
from .common import is_static, caption, display_static, show_in, close_if_inline
from .diagrams import class_diagram, nested_boxes, stacks_diagram, chain_diagram, state_diagram, tree_diagram
from .trace import trace, traced


def _buttons(items, handler, style=""):
    out = []
    for label, value in items:
        b = w.Button(description=label, button_style=style, layout=w.Layout(width="auto"))
        b.on_click(lambda _b, v=value: handler(v))
        out.append(b)
    return out


# ---------------------------------------------------------------------------
# Builder lab
# ---------------------------------------------------------------------------
class SpecSheetBuilder:
    name = "SpecSheetBuilder (text)"

    def reset(self):
        self.lines = []

    def cpu(self, model):
        self.lines.append(f"CPU      {model}")

    def ram(self, gb):
        self.lines.append(f"RAM      {gb} GB")

    def storage(self, kind, gb):
        self.lines.append(f"Storage  {gb} GB {kind}")

    def gpu(self, model):
        self.lines.append(f"GPU      {model}")

    def result(self):
        return "\n".join(self.lines) if self.lines else "(empty)"


class JsonBuilder:
    name = "JsonBuilder (dict)"

    def reset(self):
        self.data = {}

    def cpu(self, model):
        self.data["cpu"] = model

    def ram(self, gb):
        self.data["ram_gb"] = gb

    def storage(self, kind, gb):
        self.data.setdefault("storage", []).append({"kind": kind, "gb": gb})

    def gpu(self, model):
        self.data["gpu"] = model

    def result(self):
        return json.dumps(self.data, indent=2)


class Director:
    # Knows the recipes; does not know how the builder represents the product.
    def office_pc(self, b):
        b.reset(); b.cpu("i5"); b.ram(16); b.storage("SSD", 512)

    def gaming_pc(self, b):
        b.reset(); b.cpu("Ryzen 9"); b.ram(64); b.storage("NVMe", 2000); b.storage("HDD", 4000); b.gpu("RTX 4080")


STEPS = [("CPU i7", ("cpu", ("i7",))), ("RAM 32 GB", ("ram", (32,))), ("SSD 1 TB", ("storage", ("SSD", 1000))),
         ("HDD 4 TB", ("storage", ("HDD", 4000))), ("GPU RTX 4070", ("gpu", ("RTX 4070",)))]


class BuilderLab:
    def __init__(self):
        self.builders = {b.name: b for b in (SpecSheetBuilder(), JsonBuilder())}
        self.director = Director()
        self.steps = []
        self._build_ui()
        self.reset()

    def builder(self):
        return self.builders[self.kind.value]

    def reset(self):
        for b in self.builders.values():
            b.reset()
        self.steps = []
        self._render()

    def step(self, spec):
        method, args = spec
        for b in self.builders.values():          # keep both builders in sync so switching shows the same product
            getattr(b, method)(*args)
        self.steps.append(f"{method}{args}")
        self._render()

    def recipe(self, which):
        for b in self.builders.values():
            getattr(self.director, which)(b)
        self.steps = [f"director.{which}(builder)"]
        self._render()

    def diagram(self):
        return class_diagram(
            {"Director": ["+office_pc(builder)", "+gaming_pc(builder)"],
             "Builder": ["+reset()", "+cpu(model)", "+ram(gb)", "+storage(kind, gb)", "+gpu(model)", "+result()"],
             "SpecSheetBuilder": ["+result() -> str"], "JsonBuilder": ["+result() -> dict"]},
            [("SpecSheetBuilder", "Builder", "implements"), ("JsonBuilder", "Builder", "implements"), ("Director", "Builder", "uses", "drives")],
            abstract={"Builder"}, layout={"Director": (-1.2, 0), "Builder": (0.6, 0), "SpecSheetBuilder": (-0.3, 1), "JsonBuilder": (1.5, 1)},
            title="Builder: the director knows the steps, the builder knows the representation")

    def html(self):
        steps = "<br>".join(self.steps) if self.steps else "(no steps yet)"
        return (f"<div style='display:flex; gap:30px; font-family:monospace; font-size:12px'><div><b>steps taken</b><br>{steps}</div>"
                f"<div><b>product from {self.kind.value}</b><pre style='margin:0'>{self.builder().result()}</pre></div></div>")

    def _build_ui(self):
        self.kind = w.Dropdown(options=list(self.builders), description="builder", layout=w.Layout(width="260px"))
        self.kind.observe(lambda ch: self._render(), names="value")
        step_btns = _buttons([(label, spec) for label, spec in STEPS], self.step)
        recipe_btns = _buttons([("Director: office PC", "office_pc"), ("Director: gaming PC", "gaming_pc")], self.recipe, "info")
        reset = w.Button(description="Reset", button_style="danger", layout=w.Layout(width="80px"))
        reset.on_click(lambda _b: self.reset())
        self.out = w.HTML()
        header = w.HTML("<b>Builder Lab.</b> Add parts step by step, or let the Director run a recipe. Switch the builder to see the same steps produce a different representation.")
        self.ui = w.VBox([header, w.HBox([self.kind, reset]), w.HBox(step_btns), w.HBox(recipe_btns), self.out])

    def _render(self):
        self.out.value = self.html()


def builder_lab(static=None):
    """Open the Builder Lab."""
    lab = BuilderLab()
    if is_static(static):
        caption("Builder Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        lab.recipe("gaming_pc")
        display_static(lab.diagram())
        display(HTML(lab.html()))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Decorator lab
# ---------------------------------------------------------------------------
class Text:
    def __init__(self, s):
        self.s = s

    def render(self):
        return self.s


class TextDecorator:
    def __init__(self, inner):
        self.inner = inner

    def render(self):
        return self.inner.render()


class Bold(TextDecorator):
    def render(self):
        return f"**{self.inner.render()}**"


class Italic(TextDecorator):
    def render(self):
        return f"_{self.inner.render()}_"


class Upper(TextDecorator):
    def render(self):
        return self.inner.render().upper()


class Bracket(TextDecorator):
    def render(self):
        return f"[{self.inner.render()}]"


class Espresso:
    def cost(self):
        return 2.0

    def describe(self):
        return "espresso"


class Condiment:
    def __init__(self, inner):
        self.inner = inner


class Milk(Condiment):
    def cost(self):
        return self.inner.cost() + 0.5

    def describe(self):
        return self.inner.describe() + " + milk"


class Sugar(Condiment):
    def cost(self):
        return self.inner.cost() + 0.2

    def describe(self):
        return self.inner.describe() + " + sugar"


class Whip(Condiment):
    def cost(self):
        return self.inner.cost() + 0.7

    def describe(self):
        return self.inner.describe() + " + whipped cream"


DOMAINS = {
    "text": {"base": lambda: Text("hello world"), "wrappers": {"Bold": Bold, "Italic": Italic, "Upper": Upper, "Bracket": Bracket},
             "show": lambda obj: obj.render(), "core": "Text('hello world')"},
    "coffee": {"base": lambda: Espresso(), "wrappers": {"Milk": Milk, "Sugar": Sugar, "Whip": Whip},
               "show": lambda obj: f"{obj.describe()}   cost {obj.cost():.2f}", "core": "Espresso()"},
}


class DecoratorLab:
    def __init__(self, domain="text"):
        self.layers = []
        self._build_ui(domain)
        self._render()

    def build(self):
        d = DOMAINS[self.domain.value]
        obj = d["base"]()
        for name in self.layers:
            obj = d["wrappers"][name](obj)
        return obj

    def figure(self):
        d = DOMAINS[self.domain.value]
        return nested_boxes(list(reversed(self.layers)), d["core"], title="each wrapper holds the object inside it and has the same interface")

    def html(self):
        d = DOMAINS[self.domain.value]
        return f"<span style='font-family:monospace; font-size:13px'>result: {d['show'](self.build())}</span>"

    def _build_ui(self, domain):
        self.domain = w.Dropdown(options=list(DOMAINS), value=domain, description="domain", layout=w.Layout(width="180px"))
        self.wrap = w.Dropdown(options=list(DOMAINS[domain]["wrappers"]), description="wrap with", layout=w.Layout(width="200px"))
        add = w.Button(description="Add wrapper", button_style="primary", layout=w.Layout(width="110px"))
        pop = w.Button(description="Remove outer", layout=w.Layout(width="110px"))
        reset = w.Button(description="Reset", button_style="danger", layout=w.Layout(width="80px"))
        self.domain.observe(lambda ch: self._on_domain(), names="value")
        add.on_click(lambda _b: (self.layers.append(self.wrap.value), self._render()))
        pop.on_click(lambda _b: (self.layers.pop() if self.layers else None, self._render()))
        reset.on_click(lambda _b: (self.layers.clear(), self._render()))
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Decorator Lab.</b> Wrap the core object again and again. Order matters: Upper then Bold is not Bold then Upper.")
        self.ui = w.VBox([header, w.HBox([self.domain, self.wrap, add, pop, reset]), self.out, self.info])

    def _on_domain(self):
        self.layers = []
        self.wrap.options = list(DOMAINS[self.domain.value]["wrappers"])
        self._render()

    def _render(self):
        show_in(self.out, self.figure())
        self.info.value = self.html()


def decorator_lab(domain="text", static=None):
    """Open the Decorator Lab ('text' or 'coffee')."""
    lab = DecoratorLab(domain)
    if is_static(static):
        caption("Decorator Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        lab.layers = list(DOMAINS[domain]["wrappers"])[:2]
        display_static(lab.figure())
        display(HTML(lab.html()))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Flyweight lab
# ---------------------------------------------------------------------------
SPECIES = ["oak", "pine", "birch", "maple", "willow"]


class TreeType:
    def __init__(self, name):
        self.name = name
        self.color = {"oak": "green", "pine": "dark green", "birch": "light green", "maple": "red", "willow": "yellow"}[name]
        self.texture = name * 60          # stands in for a texture image: a few hundred bytes per type


class Tree:
    __slots__ = ("x", "y", "kind")

    def __init__(self, x, y, kind):
        self.x, self.y, self.kind = x, y, kind


def plant_forest(n, shared):
    types = {}
    tracemalloc.start()
    forest = []
    for i in range(n):
        name = SPECIES[i % len(SPECIES)]
        if shared:
            kind = types.get(name)
            if kind is None:
                kind = types[name] = TreeType(name)
        else:
            kind = TreeType(name)
        forest.append(Tree(i % 500, i // 500, kind))
    current, _peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return current, len(types) if shared else n


class FlyweightLab:
    def __init__(self, n=50_000):
        self._build_ui(n)
        self._render()

    def figure(self):
        n = self.n.value
        mem_no, types_no = plant_forest(n, shared=False)
        mem_yes, types_yes = plant_forest(n, shared=True)
        fig, ax = plt.subplots(figsize=(6.5, 3.2))
        ax.bar(["one TreeType per tree", "shared TreeTypes (flyweight)"], [mem_no / 1e6, mem_yes / 1e6], color=["tab:red", "tab:green"])
        for i, v in enumerate([mem_no / 1e6, mem_yes / 1e6]):
            ax.text(i, v, f"{v:.1f} MB", ha="center", va="bottom", fontsize=9)
        ax.set_ylabel("memory (MB)")
        ax.set_title(f"{n:,} trees: {types_no:,} TreeType objects vs {types_yes}", fontsize=10)
        fig.tight_layout()
        return close_if_inline(fig), f"<span style='font-family:monospace; font-size:12px'>saving: {(1 - mem_yes / mem_no):.0%}, {mem_no / n:.0f} vs {mem_yes / n:.0f} bytes per tree</span>"

    def _build_ui(self, n):
        self.n = w.IntSlider(value=n, min=1000, max=200_000, step=1000, description="trees", continuous_update=False, layout=w.Layout(width="360px"))
        self.n.observe(lambda ch: self._render(), names="value")
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Flyweight Lab.</b> Every tree needs a type (name, colour, texture). Measure the memory with and without sharing the types.")
        self.ui = w.VBox([header, self.n, self.out, self.info])

    def _render(self):
        fig, html = self.figure()
        show_in(self.out, fig)
        self.info.value = html


def flyweight_lab(n=50_000, static=None):
    """Open the Flyweight Lab."""
    lab = FlyweightLab(n)
    if is_static(static):
        caption("Flyweight Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        fig, html = lab.figure()
        display_static(fig)
        display(HTML(html))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Command lab
# ---------------------------------------------------------------------------
class Editor:
    def __init__(self):
        self.text = ""


class Command:
    def __init__(self, editor):
        self.editor = editor
        self.before = editor.text

    def undo(self):
        self.editor.text = self.before


class TypeWord(Command):
    def __init__(self, editor, word):
        super().__init__(editor)
        self.word = word

    def execute(self):
        self.editor.text = (self.editor.text + " " + self.word).strip()

    def __str__(self):
        return f"TypeWord({self.word!r})"


class UppercaseAll(Command):
    def execute(self):
        self.editor.text = self.editor.text.upper()

    def __str__(self):
        return "UppercaseAll()"


class DeleteLastWord(Command):
    def execute(self):
        self.editor.text = " ".join(self.editor.text.split()[:-1])

    def __str__(self):
        return "DeleteLastWord()"


class History:
    def __init__(self):
        self.undo_stack, self.redo_stack = [], []

    def run(self, command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            cmd = self.undo_stack.pop()
            cmd.undo()
            self.redo_stack.append(cmd)

    def redo(self):
        if self.redo_stack:
            cmd = self.redo_stack.pop()
            cmd.execute()
            self.undo_stack.append(cmd)


class CommandLab:
    def __init__(self):
        self.editor, self.history = Editor(), History()
        self._build_ui()
        self._render()

    def figure(self):
        return stacks_diagram({"undo stack": [str(c) for c in self.history.undo_stack],
                               "redo stack": [str(c) for c in self.history.redo_stack]},
                              title="each command remembers enough to reverse itself")

    def html(self):
        return f"<span style='font-family:monospace; font-size:13px'>editor text: \"{self.editor.text}\"</span>"

    def _build_ui(self):
        self.word = w.Text(value="hello", description="word", layout=w.Layout(width="200px"))
        type_btn = w.Button(description="Type word", button_style="primary", layout=w.Layout(width="100px"))
        upper = w.Button(description="Uppercase all", layout=w.Layout(width="110px"))
        delete = w.Button(description="Delete last word", layout=w.Layout(width="130px"))
        undo = w.Button(description="Undo", button_style="warning", layout=w.Layout(width="70px"))
        redo = w.Button(description="Redo", button_style="warning", layout=w.Layout(width="70px"))
        type_btn.on_click(lambda _b: (self.history.run(TypeWord(self.editor, self.word.value.strip() or "word")), self._render()))
        upper.on_click(lambda _b: (self.history.run(UppercaseAll(self.editor)), self._render()))
        delete.on_click(lambda _b: (self.history.run(DeleteLastWord(self.editor)), self._render()))
        undo.on_click(lambda _b: (self.history.undo(), self._render()))
        redo.on_click(lambda _b: (self.history.redo(), self._render()))
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Command Lab.</b> Every edit is an object with execute() and undo(). Watch the two stacks.")
        self.ui = w.VBox([header, w.HBox([self.word, type_btn, upper, delete, undo, redo]), self.info, self.out])

    def _render(self):
        show_in(self.out, self.figure())
        self.info.value = self.html()


def command_lab(static=None):
    """Open the Command Lab."""
    lab = CommandLab()
    if is_static(static):
        caption("Command Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        for word in ["design", "patterns", "rock"]:
            lab.history.run(TypeWord(lab.editor, word))
        lab.history.run(UppercaseAll(lab.editor))
        lab.history.undo()
        display(HTML(lab.html()))
        display_static(lab.figure())
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Chain of responsibility lab
# ---------------------------------------------------------------------------
class Approver:
    def __init__(self, title, limit, next_handler=None):
        self.title, self.limit, self.next = title, limit, next_handler

    def handle(self, amount, log):
        if amount <= self.limit:
            log.append(f"{self.title} approves {amount:,}")
            return self.title
        log.append(f"{self.title} cannot approve {amount:,} (limit {self.limit:,}), passing on")
        if self.next is None:
            log.append("nobody could approve it")
            return None
        return self.next.handle(amount, log)


class ChainLab:
    def __init__(self):
        self._build_ui()
        self._render()

    def run(self):
        ceo = Approver("CEO", float("inf"))
        director = Approver("Director", self.l3.value, ceo)
        manager = Approver("Manager", self.l2.value, director)
        clerk = Approver("Clerk", self.l1.value, manager)
        log = []
        handled = clerk.handle(self.amount.value, log)
        return handled, log

    def figure(self):
        handled, log = self.run()
        names = ["Clerk", "Manager", "Director", "CEO"]
        passed = names[:names.index(handled)] if handled else names
        fig = chain_diagram(names, handled_by=handled, passed=passed, title=f"request: approve {self.amount.value:,}")
        return fig, "<br>".join(log)

    def _build_ui(self):
        self.amount = w.IntSlider(value=15_000, min=0, max=100_000, step=500, description="amount", continuous_update=False, layout=w.Layout(width="360px"))
        self.l1 = w.IntSlider(value=1_000, min=0, max=100_000, step=500, description="Clerk limit", continuous_update=False, layout=w.Layout(width="300px"))
        self.l2 = w.IntSlider(value=10_000, min=0, max=100_000, step=500, description="Manager limit", continuous_update=False, layout=w.Layout(width="300px"))
        self.l3 = w.IntSlider(value=50_000, min=0, max=100_000, step=500, description="Director limit", continuous_update=False, layout=w.Layout(width="300px"))
        for s in (self.amount, self.l1, self.l2, self.l3):
            s.observe(lambda ch: self._render(), names="value")
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Chain of Responsibility Lab.</b> The request enters at the Clerk and travels until someone can approve it. The client never chooses the approver.")
        self.ui = w.VBox([header, self.amount, w.HBox([self.l1, self.l2, self.l3]), self.out, self.info])

    def _render(self):
        fig, html = self.figure()
        show_in(self.out, fig)
        self.info.value = f"<span style='font-family:monospace; font-size:12px'>{html}</span>"


def chain_lab(static=None):
    """Open the Chain of Responsibility Lab."""
    lab = ChainLab()
    if is_static(static):
        caption("Chain of Responsibility Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        fig, html = lab.figure()
        display_static(fig)
        display(HTML(f"<span style='font-family:monospace; font-size:12px'>{html}</span>"))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Observer lab
# ---------------------------------------------------------------------------
@traced
class Thermostat:
    def __init__(self):
        self.observers = []
        self.temperature = 20.0

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def set_temperature(self, value):
        self.temperature = value
        self.notify()

    def notify(self):
        for obs in list(self.observers):
            obs.update(self.temperature)


@traced
class Display:
    name = "screen"

    def __init__(self, log):
        self.log = log

    def update(self, t):
        self.log.append(f"Display shows {t:.1f} C")


@traced
class Logger:
    name = "file"

    def __init__(self, log):
        self.log = log

    def update(self, t):
        self.log.append(f"Logger writes {t:.1f} C to disk")


@traced
class Alarm:
    name = "alarm"

    def __init__(self, log, threshold):
        self.log, self.threshold = log, threshold

    def update(self, t):
        if t > self.threshold:
            self.log.append(f"Alarm: {t:.1f} C is above {self.threshold} C")
            self.ring()

    def ring(self):
        self.log.append("Alarm rings")


class ObserverLab:
    def __init__(self):
        self.log = []
        self.subject = Thermostat()
        self.instances = {}
        self._build_ui()
        self._render(initial=True)

    def sync_observers(self):
        wanted = {"Display": self.c_display.value, "Logger": self.c_logger.value, "Alarm": self.c_alarm.value}
        for name, on in wanted.items():
            if on and name not in self.instances:
                inst = {"Display": lambda: Display(self.log), "Logger": lambda: Logger(self.log),
                        "Alarm": lambda: Alarm(self.log, self.threshold.value)}[name]()
                self.instances[name] = inst
                self.subject.attach(inst)
            if not on and name in self.instances:
                self.subject.detach(self.instances.pop(name))
        if "Alarm" in self.instances:
            self.instances["Alarm"].threshold = self.threshold.value

    def run(self):
        self.sync_observers()
        self.log.clear()
        with trace() as t:
            self.subject.set_temperature(float(self.temp.value))
        return t

    def _build_ui(self):
        self.temp = w.IntSlider(value=22, min=10, max=40, step=1, description="temperature", continuous_update=False, layout=w.Layout(width="320px"))
        self.threshold = w.IntSlider(value=28, min=10, max=40, step=1, description="alarm above", continuous_update=False, layout=w.Layout(width="300px"))
        self.c_display = w.Checkbox(value=True, description="Display attached", indent=False)
        self.c_logger = w.Checkbox(value=True, description="Logger attached", indent=False)
        self.c_alarm = w.Checkbox(value=True, description="Alarm attached", indent=False)
        for widget in (self.temp, self.threshold, self.c_display, self.c_logger, self.c_alarm):
            widget.observe(lambda ch: self._render(), names="value")
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Observer Lab.</b> Move the temperature: the thermostat notifies whoever is attached. The sequence diagram is recorded from the real calls.")
        self.ui = w.VBox([header, w.HBox([self.temp, self.threshold]), w.HBox([self.c_display, self.c_logger, self.c_alarm]), self.out, self.info])

    def _render(self, initial=False):
        t = self.run()
        show_in(self.out, t.diagram(title="what happened on set_temperature"))
        self.info.value = "<span style='font-family:monospace; font-size:12px'>" + "<br>".join(self.log) + "</span>"


def observer_lab(static=None):
    """Open the Observer Lab."""
    lab = ObserverLab()
    if is_static(static):
        caption("Observer Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        lab.temp.value = 31
        t = lab.run()
        display_static(t.diagram(title="what happened on set_temperature(31)"))
        display(HTML("<span style='font-family:monospace; font-size:12px'>" + "<br>".join(lab.log) + "</span>"))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# State machine lab
# ---------------------------------------------------------------------------
MACHINES = {
    "turnstile": {"initial": "Locked",
                  "transitions": [("Locked", "coin", "Unlocked"), ("Locked", "push", "Locked"),
                                  ("Unlocked", "push", "Locked"), ("Unlocked", "coin", "Unlocked")]},
    "order": {"initial": "New",
              "transitions": [("New", "pay", "Paid"), ("New", "cancel", "Cancelled"), ("Paid", "ship", "Shipped"),
                              ("Paid", "cancel", "Cancelled"), ("Shipped", "deliver", "Delivered")]},
    "traffic light": {"initial": "Red",
                      "transitions": [("Red", "timer", "Green"), ("Green", "timer", "Yellow"), ("Yellow", "timer", "Red"),
                                      ("Green", "emergency", "Red"), ("Yellow", "emergency", "Red")]},
}


class StateMachine:
    def __init__(self, spec):
        self.transitions = {(s, e): d for s, e, d in spec["transitions"]}
        self.states = []
        for s, _e, d in spec["transitions"]:
            for x in (s, d):
                if x not in self.states:
                    self.states.append(x)
        self.state = spec["initial"]
        self.log = []

    def events(self):
        return sorted({e for _s, e in self.transitions})

    def handle(self, event):
        key = (self.state, event)
        if key in self.transitions:
            new = self.transitions[key]
            self.log.append(f"{self.state} --{event}--> {new}")
            self.state = new
        else:
            self.log.append(f"{self.state}: '{event}' is ignored here")


class StateMachineLab:
    def __init__(self, machine="turnstile"):
        self._build_ui(machine)
        self._load()

    def figure(self):
        spec = MACHINES[self.machine_dd.value]
        return state_diagram(self.machine.states, spec["transitions"], current=self.machine.state,
                             title=f"{self.machine_dd.value}: current state {self.machine.state}")

    def _build_ui(self, machine):
        self.machine_dd = w.Dropdown(options=list(MACHINES), value=machine, description="machine", layout=w.Layout(width="220px"))
        self.machine_dd.observe(lambda ch: self._load(), names="value")
        self.buttons = w.HBox()
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>State Machine Lab.</b> Fire events. The current state decides what each event does; some events are ignored in some states.")
        self.ui = w.VBox([header, self.machine_dd, self.buttons, self.out, self.info])

    def _load(self):
        self.machine = StateMachine(MACHINES[self.machine_dd.value])
        self.buttons.children = _buttons([(e, e) for e in self.machine.events()], self._fire, "primary") + \
            _buttons([("reset", None)], lambda _v: self._load(), "danger")
        self._render()

    def _fire(self, event):
        self.machine.handle(event)
        self._render()

    def _render(self):
        show_in(self.out, self.figure())
        self.info.value = "<span style='font-family:monospace; font-size:12px'>" + "<br>".join(self.machine.log[-8:]) + "</span>"


def state_machine_lab(machine="turnstile", static=None):
    """Open the State Machine Lab ('turnstile', 'order' or 'traffic light')."""
    lab = StateMachineLab(machine)
    if is_static(static):
        caption("State Machine Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        display_static(lab.figure())
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Interpreter lab
# ---------------------------------------------------------------------------
class Num:
    def __init__(self, value):
        self.value = value

    def interpret(self):
        return self.value

    def accept(self, visitor):
        return visitor.visit_num(self)


class BinOp:
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right

    def interpret(self):
        a, b = self.left.interpret(), self.right.interpret()
        return {"+": a + b, "-": a - b, "*": a * b, "/": a / b if b else float("nan")}[self.op]

    def accept(self, visitor):
        return visitor.visit_binop(self)


class PrefixPrinter:
    def visit_num(self, node):
        return f"{node.value:g}"

    def visit_binop(self, node):
        return f"({node.op} {node.left.accept(self)} {node.right.accept(self)})"


class Parser:
    # grammar:  expr := term (('+'|'-') term)*    term := factor (('*'|'/') factor)*    factor := number | '(' expr ')' | '-' factor
    def __init__(self, text):
        self.tokens = self.tokenize(text)
        self.pos = 0

    @staticmethod
    def tokenize(text):
        tokens, i = [], 0
        while i < len(text):
            ch = text[i]
            if ch.isspace():
                i += 1
            elif ch.isdigit() or ch == ".":
                j = i
                while j < len(text) and (text[j].isdigit() or text[j] == "."):
                    j += 1
                tokens.append(("num", float(text[i:j])))
                i = j
            elif ch in "+-*/()":
                tokens.append(("op", ch))
                i += 1
            else:
                raise ValueError(f"unexpected character {ch!r}")
        return tokens

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else (None, None)

    def take(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        node = self.expr()
        if self.peek()[0] is not None:
            raise ValueError("unexpected input after expression")
        return node

    def expr(self):
        node = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self.take()[1]
            node = BinOp(op, node, self.term())
        return node

    def term(self):
        node = self.factor()
        while self.peek() in (("op", "*"), ("op", "/")):
            op = self.take()[1]
            node = BinOp(op, node, self.factor())
        return node

    def factor(self):
        kind, value = self.take()
        if kind == "num":
            return Num(value)
        if (kind, value) == ("op", "("):
            node = self.expr()
            if self.take() != ("op", ")"):
                raise ValueError("missing closing parenthesis")
            return node
        if (kind, value) == ("op", "-"):
            return BinOp("-", Num(0), self.factor())
        raise ValueError("expected a number or '('")


def ast_figure(root, title=""):
    return tree_diagram(root, lambda n: [n.left, n.right] if isinstance(n, BinOp) else [],
                        lambda n: n.op if isinstance(n, BinOp) else f"{n.value:g}", title=title)


class InterpreterLab:
    def __init__(self, text="2 * (3 + 4) - 10 / 5"):
        self._build_ui(text)
        self._render()

    def result(self):
        try:
            tree = Parser(self.text.value).parse()
        except (ValueError, IndexError) as e:
            return None, f"<span style='color:#c00'>parse error: {e}</span>"
        value = tree.interpret()
        prefix = tree.accept(PrefixPrinter())
        return ast_figure(tree, title="the expression as a tree of Num and BinOp objects"), \
            f"<span style='font-family:monospace; font-size:12px'>interpret() = {value:g} &nbsp;|&nbsp; PrefixPrinter visitor: {prefix}</span>"

    def _build_ui(self, text):
        self.text = w.Text(value=text, description="expression", layout=w.Layout(width="420px"))
        self.text.observe(lambda ch: self._render(), names="value")
        self.out = w.Output()
        self.info = w.HTML()
        header = w.HTML("<b>Interpreter Lab.</b> Type an arithmetic expression. The parser builds a tree of rule objects; interpret() evaluates it and a Visitor prints it.")
        self.ui = w.VBox([header, self.text, self.out, self.info])

    def _render(self):
        fig, html = self.result()
        show_in(self.out, fig)
        self.info.value = html


def interpreter_lab(text="2 * (3 + 4) - 10 / 5", static=None):
    """Open the Interpreter Lab."""
    lab = InterpreterLab(text)
    if is_static(static):
        caption("Interpreter Lab (static preview). Run this cell in JupyterLab for the interactive version.")
        fig, html = lab.result()
        display_static(fig)
        display(HTML(html))
        return None
    display(lab.ui)
    return None


# ---------------------------------------------------------------------------
# Pattern picker
# ---------------------------------------------------------------------------
SITUATIONS = [
    ("I need exactly one shared instance of something (config, connection pool)", "Singleton (or a module)", "creational", "Ensure a class has one instance and a global point of access", "gof/01_Creational.ipynb"),
    ("The code that creates objects should not know which concrete class it gets", "Factory Method", "creational", "Defer instantiation to subclasses or a factory function", "gof/01_Creational.ipynb"),
    ("Several objects must always be created to match each other (a theme, a platform)", "Abstract Factory", "creational", "Create families of related objects without naming their classes", "gof/01_Creational.ipynb"),
    ("Constructing an object needs many optional steps and the same steps may produce different results", "Builder", "creational", "Separate construction from representation", "gof/01_Creational.ipynb"),
    ("Creating an object is expensive; I would rather copy a configured one", "Prototype", "creational", "Create new objects by copying a prototype", "gof/01_Creational.ipynb"),
    ("A class I cannot change has the wrong interface for my client", "Adapter", "structural", "Convert one interface into another the client expects", "gof/02_Structural_Part_1.ipynb"),
    ("Two dimensions vary independently and subclassing would explode (shapes x renderers)", "Bridge", "structural", "Decouple an abstraction from its implementation", "gof/02_Structural_Part_1.ipynb"),
    ("I have tree-shaped data and want to treat leaves and groups the same way", "Composite", "structural", "Compose objects into trees and treat them uniformly", "gof/02_Structural_Part_1.ipynb"),
    ("I want to add behaviour to individual objects at runtime, in combinations", "Decorator", "structural", "Attach responsibilities dynamically by wrapping", "gof/02_Structural_Part_1.ipynb"),
    ("A subsystem is too complicated for callers; I want one simple entry point", "Facade", "structural", "Provide a unified interface to a set of interfaces", "gof/03_Structural_Part_2.ipynb"),
    ("I have huge numbers of similar objects and memory is the problem", "Flyweight", "structural", "Share intrinsic state among many fine-grained objects", "gof/03_Structural_Part_2.ipynb"),
    ("I want to control access to an object: lazy creation, caching, permissions, remote calls", "Proxy", "structural", "Provide a stand-in that controls access to the real object", "gof/03_Structural_Part_2.ipynb"),
    ("A request may be handled by one of several handlers, decided at runtime", "Chain of Responsibility", "behavioural", "Pass a request along a chain until one handles it", "gof/04_Behavioral_Part_1.ipynb"),
    ("I need undo, redo, queuing or logging of operations", "Command", "behavioural", "Encapsulate a request as an object", "gof/04_Behavioral_Part_1.ipynb"),
    ("I want to walk a collection without exposing how it is stored", "Iterator", "behavioural", "Access elements sequentially without exposing the representation", "gof/04_Behavioral_Part_1.ipynb"),
    ("Many components talk to each other and the wiring is a mess", "Mediator", "behavioural", "Centralise complex communication in one object", "gof/04_Behavioral_Part_1.ipynb"),
    ("When one object changes, several others must react, and the set of them varies", "Observer", "behavioural", "One-to-many dependency with automatic notification", "gof/05_Behavioral_Part_2.ipynb"),
    ("An object's behaviour depends on its state and there are many if statements on it", "State", "behavioural", "Let an object change its behaviour when its state changes", "gof/05_Behavioral_Part_2.ipynb"),
    ("I want to swap the algorithm used for a task at runtime", "Strategy", "behavioural", "Make a family of algorithms interchangeable", "gof/05_Behavioral_Part_2.ipynb"),
    ("I need to save and restore an object's state without exposing its internals", "Memento", "behavioural", "Capture and restore internal state", "gof/05_Behavioral_Part_2.ipynb"),
    ("Several classes share an algorithm skeleton but differ in a few steps", "Template Method", "behavioural", "Define the skeleton and let subclasses redefine steps", "gof/06_Behavioral_Part_3.ipynb"),
    ("I keep adding operations over a fixed set of node types", "Visitor", "behavioural", "Add operations without changing the element classes", "gof/06_Behavioral_Part_3.ipynb"),
    ("I need to evaluate sentences in a small language (formulas, rules, queries)", "Interpreter", "behavioural", "Represent the grammar as classes and interpret sentences", "gof/06_Behavioral_Part_3.ipynb"),
]


class PatternPicker:
    def __init__(self):
        self._build_ui()
        self._render()

    def _build_ui(self):
        self.situation = w.Dropdown(options=[s[0] for s in SITUATIONS], description="my problem", layout=w.Layout(width="720px"))
        self.situation.observe(lambda ch: self._render(), names="value")
        self.info = w.HTML()
        header = w.HTML("<b>Pattern Picker.</b> Describe the pain, get the pattern. Then read its section before using it.")
        self.ui = w.VBox([header, self.situation, self.info])

    def html(self, situation=None):
        text, pattern, category, intent, where = next(s for s in SITUATIONS if s[0] == (situation or self.situation.value))
        return (f"<div style='font-size:13px; line-height:1.6'><b>{pattern}</b> &nbsp;<i>({category})</i><br>"
                f"<b>Intent:</b> {intent}<br><b>Where:</b> {where}</div>")

    def _render(self):
        self.info.value = self.html()


def pattern_picker(static=None):
    """Open the Pattern Picker."""
    lab = PatternPicker()
    if is_static(static):
        caption("Pattern Picker (static preview). Run this cell in JupyterLab for the interactive version.")
        display(HTML(lab.html(SITUATIONS[8][0])))
        return None
    display(lab.ui)
    return None
