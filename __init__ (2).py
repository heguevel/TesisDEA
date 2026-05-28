# -*- coding: utf-8 -*-
"""
dea_suite.models.mrm
---------------------
Most Restrictive Movement (MRM) model.

Objective  : Maximize LE  (largest equi-proportional improvement)
Type       : LP + SOS1  →  MIP
Reference  : Aparicio et al. (2007)

The model finds the projection of an inefficient DMU onto the
efficient frontier by maximising the minimum proportional improvement
across all inputs and outputs simultaneously, subject to lying on a
supporting hyperplane of the VRS frontier.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd

from dea_suite.data import DEADataset
from dea_suite.solvers import SolveResult, DEFAULT_SOLVER


def _solve_mrm_gurobi(ds: DEADataset, n: int) -> SolveResult:
    import gurobipy as gp
    from gurobipy import GRB

    m = gp.Model("MRM")
    m.setParam("OutputFlag", 0)

    J = range(ds.n_eff)
    I = range(ds.n_inputs)
    R = range(ds.n_outputs)

    # --- Variables -------------------------------------------------------
    lam  = m.addVars(J, lb=0.0, name="lambda")
    s_m  = m.addVars(I, lb=0.0, name="S_MENOS")
    s_p  = m.addVars(R, lb=0.0, name="S_MAS")
    V    = m.addVars(I, lb=0.0, name="V")
    U    = m.addVars(R, lb=0.0, name="U")
    h0   = m.addVar(lb=-1e20, ub=1e20, name="h0")
    k    = m.addVars(J, lb=0.0, name="k")
    LE   = m.addVar(lb=0.0, name="LE")
    Beta = m.addVar(lb=0.0, name="Beta")

    # --- Constraints -----------------------------------------------------
    # Classic VRS input constraints
    for i in I:
        m.addConstr(
            gp.quicksum(ds.x_eff(j, i) * lam[j] for j in J) + s_m[i]
            == ds.x_ineff(n, i) * Beta
        )
    # Classic VRS output constraints
    for r in R:
        m.addConstr(
            gp.quicksum(ds.y_eff(j, r) * lam[j] for j in J) - s_p[r]
            == ds.y_ineff(n, r) * Beta
        )
    # VRS convexity
    m.addConstr(gp.quicksum(lam[j] for j in J) == Beta)

    # Supporting hyperplane
    for j in J:
        m.addConstr(
            gp.quicksum(-ds.x_eff(j, i) * V[i] for i in I)
            + gp.quicksum(ds.y_eff(j, r) * U[r] for r in R)
            + h0 + k[j] == 0
        )

    # SOS1: lambda_j and k_j cannot both be non-zero
    for j in J:
        m.addSOS(GRB.SOS_TYPE1, [lam[j], k[j]])

    # V >= Beta, U >= Beta
    for i in I:
        m.addConstr(V[i] >= Beta)
    for r in R:
        m.addConstr(U[r] >= Beta)

    # Equi-proportional improvement bounds
    for i in I:
        m.addConstr(LE * ds.x_ineff(n, i) <= s_m[i])
        m.addConstr(s_m[i] / ds.x_ineff(n, i) <= 1.0)
    for r in R:
        m.addConstr(LE * ds.y_ineff(n, r) <= s_p[r])
        m.addConstr(s_p[r] / ds.y_ineff(n, r) <= 1.0)

    # --- Objective -------------------------------------------------------
    m.setObjective(LE, GRB.MAXIMIZE)
    m.optimize()

    if m.Status == GRB.OPTIMAL:
        beta_val = Beta.X if Beta.X > 1e-10 else 1.0
        vals: dict = {"LE": LE.X, "Beta": Beta.X}
        for j in J:
            vals[f"lambda_{ds.dmu_efficient[j]}"] = lam[j].X / beta_val
        for i in I:
            vals[f"S_MENOS_{ds.inputs[i]}"] = s_m[i].X / beta_val
        for r in R:
            vals[f"S_MAS_{ds.outputs[r]}"] = s_p[r].X / beta_val
        return SolveResult(
            status="optimal", objective=m.ObjVal,
            variables=vals, solver_used="gurobi"
        )
    else:
        return SolveResult(
            status="infeasible", solver_used="gurobi",
            message=f"Gurobi status: {m.Status}"
        )


def _solve_mrm_scip(ds: DEADataset, n: int) -> SolveResult:
    import pyscipopt as sp

    m = sp.Model("MRM")
    m.hideOutput()

    J = range(ds.n_eff)
    I = range(ds.n_inputs)
    R = range(ds.n_outputs)

    lam  = {j: m.addVar(lb=0.0, name=f"lambda_{j}") for j in J}
    s_m  = {i: m.addVar(lb=0.0, name=f"S_MENOS_{i}") for i in I}
    s_p  = {r: m.addVar(lb=0.0, name=f"S_MAS_{r}") for r in R}
    V    = {i: m.addVar(lb=0.0, name=f"V_{i}") for i in I}
    U    = {r: m.addVar(lb=0.0, name=f"U_{r}") for r in R}
    h0   = m.addVar(lb=-1e20, ub=1e20, name="h0")
    k    = {j: m.addVar(lb=0.0, name=f"k_{j}") for j in J}
    LE   = m.addVar(lb=0.0, name="LE")
    Beta = m.addVar(lb=0.0, name="Beta")

    for i in I:
        m.addCons(
            sp.quicksum(ds.x_eff(j, i) * lam[j] for j in J) + s_m[i]
            == ds.x_ineff(n, i) * Beta
        )
    for r in R:
        m.addCons(
            sp.quicksum(ds.y_eff(j, r) * lam[j] for j in J) - s_p[r]
            == ds.y_ineff(n, r) * Beta
        )
    m.addCons(sp.quicksum(lam[j] for j in J) == Beta)

    for j in J:
        m.addCons(
            sp.quicksum(-ds.x_eff(j, i) * V[i] for i in I)
            + sp.quicksum(ds.y_eff(j, r) * U[r] for r in R)
            + h0 + k[j] == 0
        )

    # SOS1 via big-M indicator (SCIP supports SOS natively via addConsSOS1)
    for j in J:
        m.addConsSOS1([lam[j], k[j]])

    for i in I:
        m.addCons(V[i] >= Beta)
    for r in R:
        m.addCons(U[r] >= Beta)

    for i in I:
        m.addCons(LE * ds.x_ineff(n, i) <= s_m[i])
        m.addCons(s_m[i] / ds.x_ineff(n, i) <= 1.0)
    for r in R:
        m.addCons(LE * ds.y_ineff(n, r) <= s_p[r])
        m.addCons(s_p[r] / ds.y_ineff(n, r) <= 1.0)

    m.setObjective(LE, "maximize")
    m.optimize()

    if m.getStatus() == "optimal":
        beta_val = m.getVal(Beta)
        if beta_val < 1e-10:
            beta_val = 1.0
        vals: dict = {"LE": m.getVal(LE), "Beta": beta_val}
        for j in J:
            vals[f"lambda_{ds.dmu_efficient[j]}"] = m.getVal(lam[j]) / beta_val
        for i in I:
            vals[f"S_MENOS_{ds.inputs[i]}"] = m.getVal(s_m[i]) / beta_val
        for r in R:
            vals[f"S_MAS_{ds.outputs[r]}"] = m.getVal(s_p[r]) / beta_val
        return SolveResult(
            status="optimal", objective=m.getVal(LE),
            variables=vals, solver_used="scip"
        )
    else:
        return SolveResult(
            status="infeasible", solver_used="scip",
            message=f"SCIP status: {m.getStatus()}"
        )


def solve_mrm(
    ds: DEADataset,
    n: int,
    solver: Optional[str] = None,
) -> SolveResult:
    """
    Solve the MRM model for inefficient DMU index ``n``.

    Parameters
    ----------
    ds : DEADataset
    n : int
        Zero-based index into ``ds.dmu_inefficient``.
    solver : str, optional
        "gurobi" or "scip". Defaults to first available.

    Returns
    -------
    SolveResult
    """
    s = (solver or DEFAULT_SOLVER).lower()
    if s == "gurobi":
        return _solve_mrm_gurobi(ds, n)
    elif s == "scip":
        return _solve_mrm_scip(ds, n)
    else:
        raise ValueError(f"Unknown solver '{s}'. Choose from: {['gurobi','scip']}")


def run_mrm(
    ds: DEADataset,
    solver: Optional[str] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Run MRM for all inefficient DMUs and return a results DataFrame.

    Parameters
    ----------
    ds : DEADataset
    solver : str, optional
    verbose : bool
        Print progress to stdout.

    Returns
    -------
    pd.DataFrame
        One row per inefficient DMU, columns: Obj Value, lambda_*,
        S_MENOS_*, S_MAS_*, Cambio_*, TARGET_*, Sum_Cambio.
    """
    report = ds.data_ineff.copy()

    for n in range(ds.n_ineff):
        dmu_name = ds.dmu_inefficient[n]
        result = solve_mrm(ds, n, solver=solver)

        if not result.is_optimal:
            if verbose:
                print(f"  [MRM] {dmu_name}: {result.status} — {result.message}")
            continue

        if verbose:
            print(f"  [MRM] {dmu_name}: LE = {result.objective:.6f}")

        report.loc[n, "Obj Value (LE)"] = result.objective

        for dmu in ds.dmu_efficient:
            report.loc[n, f"lambda_{dmu}"] = result.get(f"lambda_{dmu}")
        for inp in ds.inputs:
            report.loc[n, f"S_MENOS_{inp}"] = result.get(f"S_MENOS_{inp}")
        for out in ds.outputs:
            report.loc[n, f"S_MAS_{out}"] = result.get(f"S_MAS_{out}")

        for inp in ds.inputs:
            x0 = ds.x_ineff(n, ds.inputs.index(inp))
            s  = result.get(f"S_MENOS_{inp}")
            report.loc[n, f"Cambio_{inp}"]  = s / x0 if x0 > 0 else None
            report.loc[n, f"TARGET_{inp}"]  = x0 - s

        for out in ds.outputs:
            y0 = ds.y_ineff(n, ds.outputs.index(out))
            s  = result.get(f"S_MAS_{out}")
            report.loc[n, f"Cambio_{out}"]  = s / y0 if y0 > 0 else None
            report.loc[n, f"TARGET_{out}"]  = y0 + s

        cambio_cols = [f"Cambio_{v}" for v in ds.inputs + ds.outputs]
        report.loc[n, "Sum_Cambio"] = report.loc[n, cambio_cols].sum()

    return report
