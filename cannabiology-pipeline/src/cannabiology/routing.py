"""Routing gate. Runs before any generation and cannot be bypassed.

Six production routes. Rules are declarative (config/routing_rules.yaml),
ordered, and ESCALATION-ONLY: a rule may make a figure stricter, never looser.
No figure is downgraded to GENERATE because a model could make it look plausible.
"""
import re
from dataclasses import dataclass

from . import config

GENERATE = "GENERATE"
HYBRID = "HYBRID"
VECTOR_BUILD = "VECTOR_BUILD"
DATA_DRIVEN = "DATA_DRIVEN"
HUMAN_BUILD = "HUMAN_BUILD"
HOLD = "HOLD"

# Routes that may ever call an image-generation model for their substantive content.
GENERATIVE_ROUTES = {GENERATE, HYBRID}
# Routes that must never be entered by the automated generation loop.
BLOCKED_FROM_GENERATION = {VECTOR_BUILD, DATA_DRIVEN, HUMAN_BUILD, HOLD}


@dataclass
class RoutingDecision:
    figure_id: str
    route: str
    confidence: str          # "explicit" | "derived"
    reasons: list
    needs_route_confirmation: bool

    def may_generate(self):
        return self.route in GENERATIVE_ROUTES and not self.needs_route_confirmation


class Router:
    def __init__(self, rules=None):
        self.rules = rules or config.routing_rules()
        self.rank = {r: i for i, r in enumerate(self.rules["strictness"])}

    def _escalate(self, current, candidate):
        if current is None:
            return candidate
        return candidate if self.rank[candidate] > self.rank[current] else current

    def route(self, fig):
        route, confidence, reasons = None, "derived", []
        needs_confirm = False

        for rule in self.rules["explicit_status"]:
            if re.search(rule["match"], fig.status, re.I):
                route = self._escalate(route, rule["route"])
                confidence = "explicit"
                reasons.append(rule["reason"])
                break

        for rule in self.rules["scientific_escalation"]:
            if re.search(rule["match"], fig.science_notes, re.I):
                new = self._escalate(route, rule["route"])
                if new != route:
                    reasons.append(rule["reason"])
                    route = new

        if confidence == "derived":
            for rule in self.rules["visual_type_escalation"]:
                if re.search(rule["match"], fig.visual_type, re.I):
                    new = self._escalate(route, rule["route"])
                    if new != route:
                        reasons.append(rule["reason"])
                        route = new

        if route is None:
            fb = self.rules["fallback"]
            route = fb["route"]
            reasons.append(fb["reason"])
            needs_confirm = bool(fb.get("needs_route_confirmation"))

        hu = self.rules["hybrid_upgrade"]
        if hu.get("when_labels_present") and fig.manual_labels and route == GENERATE:
            route = HYBRID
            reasons.append(hu["reason"])

        if confidence == "derived" and route in GENERATIVE_ROUTES:
            needs_confirm = True

        return RoutingDecision(fig.figure_id, route, confidence, reasons, needs_confirm)

    def route_all(self, figures):
        return {fid: self.route(f) for fid, f in figures.items()}
