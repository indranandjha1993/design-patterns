"""Checkpoint quizzes: banks 1 to 7 for the Gang of Four track, arch1 to arch5 for the architecture track."""
import html
import ipywidgets as w
from IPython.display import display
from .common import is_static, caption

QUESTIONS = {
    1: [
        ("Which pattern lets a base class define the steps of creating an object while subclasses decide which concrete class to instantiate?",
         ["Singleton", "Factory Method", "Builder", "Prototype"], 1,
         "Factory Method: the creator calls an overridable method that returns the product."),
        ("Abstract Factory differs from Factory Method because it creates",
         ["one object of one type", "families of related objects that must be used together", "copies of an existing object", "exactly one instance"], 1,
         "A GUI factory returns matching buttons, checkboxes and menus for one look and feel."),
        ("Builder is the right choice when",
         ["an object needs many optional parts assembled step by step", "you need one global instance", "you need to copy an object", "a class hierarchy has too many subclasses"], 0,
         "Same construction steps, different builders, different representations."),
        ("The usual objection to Singleton is",
         ["it is slow", "it is hidden global state that makes tests depend on each other", "Python cannot express it", "it uses too much memory"], 1,
         "Prefer passing dependencies explicitly, or a module-level instance you can swap in tests."),
    ],
    2: [
        ("Adapter",
         ["adds behaviour to an object at runtime", "makes an existing class fit the interface a client expects", "splits a hierarchy in two", "treats groups and single objects alike"], 1,
         "Neither the client nor the adaptee changes; the adapter translates."),
        ("Bridge separates",
         ["interface from implementation so both can vary independently", "reads from writes", "creation from use", "the view from the model"], 0,
         "Shapes times renderers becomes shapes plus renderers: no class explosion."),
        ("Composite lets a client",
         ["undo operations", "treat individual objects and groups of objects uniformly", "share objects to save memory", "observe changes"], 1,
         "A folder and a file both answer size(); the folder sums its children."),
        ("Decorator adds responsibilities",
         ["by subclassing at compile time", "by wrapping an object with another object of the same interface", "by editing the class", "through a global registry"], 1,
         "Wrappers can be stacked in any order and chosen at runtime."),
    ],
    3: [
        ("Facade",
         ["hides a complex subsystem behind one simple entry point", "copies objects", "shares state between objects", "queues requests"], 0,
         "The subsystem is still there; the facade is the convenient front door."),
        ("Flyweight saves memory by",
         ["compressing objects", "sharing the intrinsic (unchanging) state among many objects", "deleting unused objects", "lazy loading"], 1,
         "Ten thousand trees share five tree types; only position stays per tree."),
        ("A virtual proxy",
         ["checks permissions", "delays creating an expensive object until it is really needed", "caches results", "forwards calls over the network"], 1,
         "Same interface as the real object, so the client never knows."),
        ("Which Python feature makes a forwarding Proxy almost free to write?",
         ["__getattr__", "__init__", "@staticmethod", "list comprehensions"], 0,
         "Anything not defined on the proxy falls through __getattr__ to the wrapped object."),
    ],
    4: [
        ("Chain of Responsibility",
         ["broadcasts a request to all handlers", "passes a request along handlers until one handles it", "stores requests for undo", "iterates a collection"], 1,
         "Each handler decides: handle it, or pass it on. The client does not know who handled it."),
        ("Turning a request into a Command object makes it possible to",
         ["run it faster", "queue, log and undo it", "avoid classes", "share state"], 1,
         "A command carries everything needed to execute, and to reverse, later."),
        ("Python generators are a built-in form of",
         ["Iterator", "Mediator", "Command", "Facade"], 0,
         "yield produces items one at a time on demand; for loops consume them."),
        ("Mediator exists to",
         ["replace many-to-many links between components with one hub", "create objects", "wrap objects", "store snapshots"], 0,
         "Components talk to the mediator, not to each other."),
    ],
    5: [
        ("Observer",
         ["lets one object notify many dependents when it changes", "copies objects", "chains handlers", "adds behaviour"], 0,
         "Subject keeps a list of observers and calls them; it does not know what they do."),
        ("The State pattern changes an object's behaviour by",
         ["a chain of if statements", "delegating to a state object and swapping it on transitions", "subclassing the context", "copying the object"], 1,
         "Each state is a class; transitions replace the current state object."),
        ("The most Pythonic Strategy is often",
         ["an abstract base class with one method", "a plain function passed as an argument", "a singleton", "a metaclass"], 1,
         "sorted(key=...) is Strategy: the key function is the strategy."),
        ("A Memento stores",
         ["a snapshot of an object's state without exposing its internals", "the command history", "a shared flyweight", "a proxy"], 0,
         "The originator creates and restores mementos; a caretaker just holds them."),
    ],
    6: [
        ("Template Method",
         ["fixes the skeleton of an algorithm in a base class and lets subclasses fill in steps", "copies templates", "wraps objects", "queues commands"], 0,
         "The base class calls the steps in order; subclasses override some of them."),
        ("Visitor lets you",
         ["add new element classes easily", "add new operations over a fixed set of element classes without changing them", "share elements", "undo operations"], 1,
         "Each visitor is one operation; each element's accept() dispatches to the right visit method."),
        ("The trick that makes Visitor work is",
         ["single dispatch", "double dispatch: accept() calls visit_X() chosen by both element and visitor", "reflection", "global state"], 1,
         "The element knows its own type, the visitor knows the operation."),
        ("Interpreter represents",
         ["a user interface", "grammar rules as classes and evaluates sentences by walking the tree", "a network protocol", "a queue"], 1,
         "Each rule is a class with an interpret() method; a parser builds the tree."),
    ],
    7: [
        ("The Pythonic Singleton is",
         ["a metaclass", "a module: imported once, shared everywhere", "a class with __new__ tricks", "a global list"], 1,
         "Modules are already singletons. Use one, and keep it swappable for tests."),
        ("Python's @decorator syntax is the language form of which pattern?",
         ["Decorator", "Adapter", "Proxy", "Facade"], 0,
         "A function wrapping a function with the same signature is exactly the pattern."),
        ("When should you apply a design pattern?",
         ["at the start of every project", "when you actually have the problem it solves", "whenever a class has more than three methods", "never"], 1,
         "Speculative patterns add indirection with no payoff. Refactor towards a pattern when the pain appears."),
        ("'Prefer composition over inheritance' is the principle behind",
         ["Strategy, Decorator and Bridge", "Singleton", "Template Method only", "Iterator"], 0,
         "Those patterns swap collaborators at runtime instead of fixing behaviour in a class hierarchy."),
    ],
    "arch1": [
        ("A monolith is",
         ["an old application", "one deployable unit that contains all the functionality", "a database", "a service mesh"], 1,
         "One process, one deploy, one codebase. Simple to run, and fine for most teams for a long time."),
        ("The main risk as a monolith grows is",
         ["it uses more CPU", "dependencies between parts tangle until every change is risky", "it cannot use a database", "it cannot be tested"], 1,
         "The 'big ball of mud': nothing stops module A reaching into module B's internals."),
        ("A modular monolith",
         ["splits the app into services", "keeps one deployable but enforces module boundaries with explicit interfaces", "removes the database", "has no modules"], 1,
         "You get most of the design benefits of services without the network."),
        ("Shipping a one-line fix in a monolith means",
         ["deploying only that line", "redeploying the whole application", "restarting the database", "nothing"], 1,
         "That is the cost of one deployable; with good CI it is often acceptable."),
    ],
    "arch2": [
        ("In a layered architecture, dependencies point",
         ["in any direction", "downward only: UI to service to data", "upward only", "sideways"], 1,
         "A lower layer never imports an upper one; that is what makes layers replaceable."),
        ("In hexagonal architecture a 'port' is",
         ["a network socket", "an interface the core defines and adapters implement", "a database table", "a UI screen"], 1,
         "The core owns the port; the database adapter and the in-memory test adapter both implement it."),
        ("The practical payoff of ports and adapters is",
         ["fewer files", "the core logic is testable without databases or web frameworks", "faster network calls", "no need for interfaces"], 1,
         "Swap the adapter, keep the core untouched."),
        ("In MVC the view refreshes when",
         ["the user asks", "the model changes and notifies it", "the controller is created", "the server restarts"], 1,
         "MVC is Observer applied to user interfaces."),
    ],
    "arch3": [
        ("Each microservice should",
         ["share one database with the others", "own its data and be deployable independently", "be written in the same language", "be as small as a function"], 1,
         "Shared databases couple services at the schema; independent deploys are the whole point."),
        ("A request that passes through 5 services that are each 99 percent available succeeds about",
         ["99 percent of the time", "95 percent of the time", "90 percent of the time", "always"], 1,
         "0.99 to the power 5 is 0.951. Availability multiplies along a chain."),
        ("A 'distributed monolith' is",
         ["a monolith on many machines", "services so coupled that they must be deployed together", "a modular monolith", "a service mesh"], 1,
         "The network cost of microservices without the independence benefit: the worst of both."),
        ("A circuit breaker",
         ["retries forever", "stops calling a failing dependency for a while so failures do not cascade", "encrypts traffic", "balances load"], 1,
         "Fail fast, give the dependency time to recover, probe occasionally."),
    ],
    "arch4": [
        ("In publish/subscribe the publisher",
         ["waits for each subscriber", "does not know who consumes the event", "calls subscribers directly", "must be a database"], 1,
         "That decoupling is what lets you add consumers without touching producers."),
        ("Eventual consistency means",
         ["data is never consistent", "read models lag behind writes for a short time before catching up", "writes are lost", "reads are slow"], 1,
         "The dashboard may show the old count for a moment; the events will arrive."),
        ("CQRS",
         ["encrypts queries", "separates the write model from one or more read models", "removes the database", "is the same as REST"], 1,
         "Writes validate and emit events; read models are shaped for each screen."),
        ("A saga coordinates a multi-service transaction by",
         ["one big database lock", "a sequence of local transactions with compensating actions on failure", "retrying forever", "ignoring failures"], 1,
         "Reserve stock, charge the card; if the charge fails, release the stock."),
    ],
    "arch5": [
        ("The strangler fig approach",
         ["rewrites everything at once", "gradually replaces parts of a legacy system behind a routing layer", "deletes the legacy system", "adds more services"], 1,
         "New functionality grows around the old system until the old one can be removed."),
        ("For a small team with an unclear domain, the best starting point is usually",
         ["microservices", "a modular monolith", "serverless functions everywhere", "no architecture"], 1,
         "Cheap to run, easy to refactor as the boundaries become clear, and splittable later."),
        ("Microservices pay off mainly when",
         ["the codebase is large", "teams need to deploy and scale parts independently", "the language is Python", "there is one developer"], 1,
         "Organisational independence is the driver; technical size alone is not."),
        ("Conway's law says",
         ["systems get slower over time", "a system's structure mirrors the communication structure of the organisation that builds it", "code must be documented", "services must be small"], 1,
         "Which is why team boundaries and service boundaries tend to match."),
    ],
}

TITLES = {"arch1": "Architecture 1", "arch2": "Architecture 2", "arch3": "Architecture 3", "arch4": "Architecture 4", "arch5": "Architecture 5"}


def quiz_label(key):
    return f"Module {key}" if isinstance(key, int) else TITLES.get(key, str(key))


class Quiz:
    def __init__(self, key):
        if key not in QUESTIONS:
            raise ValueError(f"no quiz for {key}")
        self.key = key
        self.items = QUESTIONS[key]
        self.correct = 0
        self.answered = 0
        self._build_ui()

    def _build_ui(self):
        blocks = []
        self.score = w.HTML()
        for i, (text, options, answer, why) in enumerate(self.items, start=1):
            q = w.HTML(f"<b>Q{i}.</b> {html.escape(text)}")
            radio = w.RadioButtons(options=options, value=None, layout=w.Layout(width="auto"))
            check = w.Button(description="Check", layout=w.Layout(width="80px"))
            feedback = w.HTML()
            check.on_click(lambda _b, r=radio, c=check, f=feedback, a=answer, why=why, opts=options: self._check(r, c, f, a, why, opts))
            blocks.append(w.VBox([q, radio, w.HBox([check, feedback])], layout=w.Layout(margin="0 0 12px 0")))
        header = w.HTML(f"<b>Checkpoint quiz, {quiz_label(self.key)}.</b> {len(self.items)} questions. Pick an answer and press Check.")
        self.ui = w.VBox([header] + blocks + [self.score])
        self._update_score()

    def _check(self, radio, check, feedback, answer, why, options):
        if radio.value is None:
            feedback.value = "<span style='color:#c00'>Pick an answer first.</span>"
            return
        chosen = options.index(radio.value)
        self.answered += 1
        if chosen == answer:
            self.correct += 1
            feedback.value = f"<span style='color:#080'><b>Correct.</b> {html.escape(why)}</span>"
        else:
            feedback.value = (f"<span style='color:#c00'><b>Not quite.</b> The answer is \"{html.escape(options[answer])}\". "
                              f"{html.escape(why)}</span>")
        radio.disabled = True
        check.disabled = True
        self._update_score()

    def _update_score(self):
        n = len(self.items)
        if self.answered == n:
            note = " Well done, move on." if self.correct == n else " Re-read the sections for the ones you missed before moving on."
            self.score.value = f"<b>Score: {self.correct} / {n}.</b>{note}"
        else:
            self.score.value = f"<b>Score so far: {self.correct} / {self.answered}</b> (of {n})"


def quiz(key, static=None):
    """Show a checkpoint quiz: 1 to 7 for the Gang of Four track, 'arch1' to 'arch5' for architecture."""
    q = Quiz(key)
    if is_static(static):
        caption(f"Checkpoint quiz, {quiz_label(key)} (static preview). Run this cell in JupyterLab to answer interactively.")
        for i, (text, options, _a, _w) in enumerate(q.items, start=1):
            caption(f"\nQ{i}. {text}")
            for j, opt in enumerate(options):
                caption(f"    {'abcd'[j]}) {opt}")
        return None
    display(q.ui)
    return None
