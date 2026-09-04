# Design Patterns

[![Read online](https://img.shields.io/badge/read%20online-github%20pages-blue)](https://indranandjha1993.github.io/design-patterns/) [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/indranandjha1993/design-patterns/main?urlpath=lab/tree/src/00_Start_Here.ipynb)

A hands-on course in two tracks. Track one covers the 23 Gang of Four patterns; track two covers the
architectures those objects live in: monoliths, modular monoliths, layered and hexagonal designs,
microservices, and event-driven systems. Every pattern comes as a class diagram, a short Python
implementation, a sequence diagram traced from the real method calls, and a lab you drive yourself.

## Read or run it

- **Read online:** https://indranandjha1993.github.io/design-patterns/ is the full course as a website, built from these notebooks on every push.
- **Run online:** the Binder badge above opens the notebooks in a live JupyterLab in your browser, labs included. The first launch after a change takes a few minutes while the image builds; later launches are quick.
- **Run locally:** see Setup below.

## Course map

Start with `src/00_Start_Here.ipynb`: environment check, the diagram legend, the call tracer, and links to both tracks.

### Track 1: Gang of Four (`src/gof/`)

| # | Notebook | Patterns |
|---|----------|----------|
| 1 | `01_Creational` | Singleton, Factory Method, Abstract Factory, Builder, Prototype |
| 2 | `02_Structural_Part_1` | Adapter, Bridge, Composite, Decorator |
| 3 | `03_Structural_Part_2` | Facade, Flyweight, Proxy |
| 4 | `04_Behavioral_Part_1` | Chain of Responsibility, Command, Iterator, Mediator |
| 5 | `05_Behavioral_Part_2` | Observer, State, Strategy, Memento |
| 6 | `06_Behavioral_Part_3` | Template Method, Visitor, Interpreter |
| 7 | `07_Patterns_in_Python` | What the language gives you for free, anti-patterns, a four-pattern capstone |

### Track 2: Architecture (`src/architecture/`)

| # | Notebook | What you learn |
|---|----------|----------------|
| 1 | `01_Monolith_and_Modular_Monolith` | One deployable, the big ball of mud, enforced module boundaries, blast radius |
| 2 | `02_Layered_Hexagonal_and_MVC` | Dependency direction, ports and adapters, testing the core without a database, MVC |
| 3 | `03_Microservices` | Data ownership, availability arithmetic, latency simulator, timeouts, retries, circuit breakers |
| 4 | `04_Event_Driven_and_CQRS` | Publish/subscribe, eventual consistency, CQRS read models, sagas |
| 5 | `05_Choosing_an_Architecture` | Trade-off table, the migration path, strangler fig, Conway's law |

Each module has learning objectives, one section per pattern (problem, structure, code, trace, when to use it),
an interactive lab, exercises with hidden solutions, a checkpoint quiz and key takeaways.

## The helper package and the labs

`src/dplab/` is installed into the project's environment by `uv sync`, so it imports from either track folder.

| Helper | What it does |
|--------|--------------|
| `class_diagram`, `sequence_diagram`, `state_diagram`, `tree_diagram`, `component_diagram` | Diagram drawers with a minimal notation |
| `@traced` and `with trace() as t:` | Record the method calls made inside the block and draw them with `t.diagram()` |
| `check_dependencies` | A few-line module boundary checker for the modular monolith |
| `quiz(key)` | Checkpoint quizzes, `1` to `7` and `'arch1'` to `'arch5'` |

| Lab | Used in |
|-----|---------|
| Pattern Picker | Start Here, GoF 7 |
| Builder Lab | GoF 1 |
| Decorator Lab | GoF 2 |
| Flyweight Lab | GoF 3 |
| Chain of Responsibility Lab, Command Lab | GoF 4 |
| Observer Lab, State Machine Lab | GoF 5 |
| Interpreter Lab | GoF 6 |
| Latency and Availability Lab | Architecture 3 |
| Event Lab | Architecture 4 |
| Architecture Picker | Architecture 5 |

Labs need a running kernel; viewed statically the notebooks show a preview of the initial state instead.

## Setup

Requires Python 3.13 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync                                                          # creates .venv with matplotlib and ipywidgets, installs dplab
uv run python -m ipykernel install --user --name design_patterns
jupyter lab src/                                                 # then pick the design_patterns kernel
```

## Editing the course

The notebooks are the source of truth: edit them in JupyterLab. If you add or reorder modules, keep the navigation
links at the top and bottom of each notebook pointing at the right neighbours and at `../00_Start_Here.ipynb`,
and update the course maps there and in this README.

## Related courses

This is one of three hands-on notebook courses built in the same format:

- [Quantum Computing with Code](https://github.com/indranandjha1993/quantum-computing): qubits to Grover and noise, with Qiskit
- [Data Structures and Algorithms](https://github.com/indranandjha1993/data-structures-algorithms): Big-O to dynamic programming, every claim measured

## License

MIT. Use it, fork it, teach with it.
