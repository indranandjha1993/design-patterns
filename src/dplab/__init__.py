"""Helpers and interactive labs for the design patterns course.

    from dplab import class_diagram, sequence_diagram, state_diagram, tree_diagram, trace, traced, quiz
    from dplab import builder_lab, decorator_lab, flyweight_lab, command_lab, chain_lab
    from dplab import observer_lab, state_machine_lab, interpreter_lab, pattern_picker
    from dplab import component_diagram, check_dependencies, latency_lab, event_lab, architecture_picker
"""
from .diagrams import class_diagram, sequence_diagram, state_diagram, tree_diagram, chain_diagram, stacks_diagram, nested_boxes
from .trace import trace, traced, Tracer
from .quiz import quiz, QUESTIONS
from .labs import (builder_lab, decorator_lab, flyweight_lab, command_lab, chain_lab, observer_lab,
                   state_machine_lab, interpreter_lab, pattern_picker, SITUATIONS, MACHINES, StateMachine, Parser, ast_figure)
from .arch import (component_diagram, check_dependencies, simulate_requests, latency_lab, event_lab, architecture_picker,
                   EventBus, OrderWriteModel, DashboardReadModel, score_architectures)

__all__ = ["class_diagram", "sequence_diagram", "state_diagram", "tree_diagram", "chain_diagram", "stacks_diagram", "nested_boxes",
           "trace", "traced", "Tracer", "quiz", "QUESTIONS",
           "builder_lab", "decorator_lab", "flyweight_lab", "command_lab", "chain_lab", "observer_lab",
           "state_machine_lab", "interpreter_lab", "pattern_picker", "SITUATIONS", "MACHINES", "StateMachine", "Parser", "ast_figure",
           "component_diagram", "check_dependencies", "simulate_requests", "latency_lab", "event_lab", "architecture_picker",
           "EventBus", "OrderWriteModel", "DashboardReadModel", "score_architectures"]
