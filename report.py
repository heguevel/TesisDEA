# -*- coding: utf-8 -*-
"""
dea_suite.solvers
-----------------
Solver abstraction layer.  Tries Gurobi first (full MIQCP support),
falls back to SCIP via pyscipopt for LP/MIP/QP problems.

Supported problem types
    - LP   : linear objective, linear constraints
    - MIP  : LP + integrality / SOS
    - QP   : quadratic objective, linear constraints
    - MIQCP: QP + integrality / SOS  (requires Gurobi or SCIP)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any

AVAILABLE_SOLVERS: list[str] = []

# ----- Try Gurobi -----
try:
    import gurobipy as gp  # type: ignore
    from gurobipy import GRB  # type: ignore
    AVAILABLE_SOLVERS.append("gurobi")
except ImportError:
    gp = None  # type: ignore

# ----- Try SCIP -----
try:
    import pyscipopt as scip_mod  # type: ignore
    AVAILABLE_SOLVERS.append("scip")
except ImportError:
    scip_mod = None  # type: ignore

if not AVAILABLE_SOLVERS:
    raise ImportError(
        "No supported solver found.\n"
        "Install at least one of:\n"
        "  pip install gurobipy        (requires Gurobi licence)\n"
        "  pip install pyscipopt       (open-source, no licence needed)\n"
    )

DEFAULT_SOLVER = AVAILABLE_SOLVERS[0]


@dataclass
class SolveResult:
    """Unified result object returned by every model."""
    status: str                          # "optimal" | "infeasible" | "error"
    objective: float | None = None
    variables: Dict[str, float] = field(default_factory=dict)
    solver_used: str = ""
    message: str = ""

    @property
    def is_optimal(self) -> bool:
        return self.status == "optimal"

    def get(self, name: str, default: float = 0.0) -> float:
        return self.variables.get(name, default)


def available_solvers() -> list[str]:
    return list(AVAILABLE_SOLVERS)
