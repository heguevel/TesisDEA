# -*- coding: utf-8 -*-
"""
dea_suite
=========
A Python package implementing three DEA projection models:

- MRM    : Most Restrictive Movement (LP + SOS1)
- DMESM  : Distance Minimising Equal-Slack Movement (QP + SOS1)
- DMISM  : Distance Minimising Individual-Slack Movement (QP + SOS1 + binary)

Supported solvers (auto-detected):
  - Gurobi  (gurobipy)   — requires licence; academic licence is free
  - SCIP    (pyscipopt)  — fully open-source, no licence required
"""

__version__ = "1.1.0"
__author__  = "DEA Suite"

from dea_suite.data    import load_dataset, DEADataset
from dea_suite.solvers import available_solvers, SolveResult
from dea_suite.report  import save_report
from dea_suite.models  import (
    run_mrm,   solve_mrm,
    run_dmesm, solve_dmesm,
    run_dmism, solve_dmism,
)

def launch_ui(host: str = "127.0.0.1", port: int = 5000, open_browser: bool = True) -> None:
    """Start the DEA Suite web UI at http://localhost:5000"""
    from dea_suite.ui.server import launch
    launch(host=host, port=port, open_browser=open_browser)

__all__ = [
    "load_dataset", "DEADataset",
    "available_solvers", "SolveResult",
    "save_report",
    "run_mrm",   "solve_mrm",
    "run_dmesm", "solve_dmesm",
    "run_dmism", "solve_dmism",
    "launch_ui",
]
