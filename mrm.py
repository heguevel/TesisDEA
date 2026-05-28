# -*- coding: utf-8 -*-
"""
dea_suite.models.dmesm
-----------------------
Distance Minimising Equal-Slack Movement (DMESM) model.

Objective  : Minimize  sum_i (d_i - d_prom)^2
Type       : QP + SOS1  →  MIQCP
Reference  : Aparicio et al.

Projects an inefficient DMU onto the efficient frontier by minimising
the variance of the proportional input/output movements, favouring
balanced projections over purely radial ones.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd

from dea_suite.data import DEADataset
from dea_suite.solvers import SolveResult, DEFAULT_SOLVER


def _solve_dmesm_gurobi(ds: DEADataset, n: int) -> SolveResult:
    import gurobipy as gp
    from gurobipy import GRB

    m = gp.Model("DMESM")
    m.setParam("OutputFlag", 0)

    J  = range(ds.n_eff)
    I  = range(ds.n_inputs)
    R  = range(ds.n_outputs)
    NV = ds.n_inputs + ds.n_outputs
    vars2 = ds.inputs + ds.outputs

    lam    = m.addVars(J, lb=0.0, name="lambda")
    s_m    = m.addVars(I, lb=0.0, name="S_MENOS")
    s_p    = m.addVars(R, lb=0.0, name="S_MAS")
    V      = m.addVars(I, lb=1.0, name="V")
    U      = m.addVars(R, lb=1.0, name="U")
    h0     = m.addVar(lb=-1e20, ub=1e20, name="h0")
    k      = m.addVars(J, lb=0.0, name="k")
    d_prom = m.addVar(lb=0.0, name="d_prom")
    d      = m.addVars(range(NV), lb=0.0, name="d")

    # Classic VRS constraints
    for i in I:
        m.addConstr(
            gp.quicksum(ds.x_eff(j, i) * lam[j] for j in J) + s_m[i]
            == ds.x_ineff(n, i)
        )
    for r in R:
        m.addConstr(
            gp.quicksum(ds.y_eff(j, r) * lam[j] for j in J) - s_p[r]
            == ds.y_ineff(n, r)
        )
    m.addConstr(gp.quicksum(lam[j] for j in J) == 1)

    # Supporting hyperplane
    for j in J:
        m.addConstr(
            gp.quicksum(-ds.x_eff(j, i) * V[i] for i in I)
            + gp.quicksum(ds.y_eff(j, r) * U[r] for r in R)
            + h0 + k[j] == 0
        )

    # SOS1
    for j in J:
        m.addSOS(GRB.SOS_TYPE1, [lam[j], k[j]])

    # Relative distance definitions: d_i = s_i / x_i (or y_r)
    for i in I:
        xi = ds.x_ineff(n, i)
        m.addConstr(d[i] * xi == s_m[i])
    for r in R:
        yr = ds.y_ineff(n, r)
        m.addConstr(d[ds.n_inputs + r] * yr == s_p[r])

    # Average distance
    m.addConstr(gp.quicksum(d[v] for v in range(NV)) == NV * d_prom)

    # Objective: minimise variance of d
    obj = gp.quicksum((d[v] - d_prom) * (d[v] - d_prom) for v in range(NV))
    m.setObjective(obj, GRB.MINIMIZE)
    m.optimize()

    if m.Status == GRB.OPTIMAL:
        vals: dict = {"d_prom": d_prom.X}
        for j in J:
            vals[f"lambda_{ds.dmu_efficient[j]}"] = lam[j].X
        for i in I:
            vals[f"S_MENOS_{ds.inputs[i]}"] = s_m[i].X
            vals[f"d_{ds.inputs[i]}"]        = d[i].X
        for r in R:
            vals[f"S_MAS_{ds.outputs[r]}"]   = s_p[r].X
            vals[f"d_{ds.outputs[r]}"]        = d[ds.n_inputs + r].X
        return SolveResult(
            status="optimal", objective=m.ObjVal,
            variables=vals, solver_used="gurobi"
        )
    else:
        return SolveResult(
            status="infeasible", solver_used="gurobi",
            message=f"Gurobi status: {m.Status}"
        )


def _solve_dmesm_scip(ds: DEADataset, n: int) -> SolveResult:
    import pyscipopt as sp

    m = sp.Model("DMESM")
    m.hideOutput()

    J  = range(ds.n_eff)
    I  = range(ds.n_inputs)
    R  = range(ds.n_outputs)
    NV = ds.n_inputs + ds.n_outputs

    lam    = {j: m.addVar(lb=0.0, name=f"lambda_{j}") for j in J}
    s_m    = {i: m.addVar(lb=0.0, name=f"S_MENOS_{i}") for i in I}
    s_p    = {r: m.addVar(lb=0.0, name=f"S_MAS_{r}") for r in R}
    V      = {i: m.addVar(lb=1.0, name=f"V_{i}") for i in I}
    U      = {r: m.addVar(lb=1.0, name=f"U_{r}") for r in R}
    h0     = m.addVar(lb=-1e20, ub=1e20, name="h0")
    k      = {j: m.addVar(lb=0.0, name=f"k_{j}") for j in J}
    d_prom = m.addVar(lb=0.0, name="d_prom")
    d      = {v: m.addVar(lb=0.0, name=f"d_{v}") for v in range(NV)}

    for i in I:
        m.addCons(
            sp.quicksum(ds.x_eff(j, i) * lam[j] for j in J) + s_m[i]
            == ds.x_ineff(n, i)
        )
    for r in R:
        m.addCons(
            sp.quicksum(ds.y_eff(j, r) * lam[j] for j in J) - s_p[r]
            == ds.y_ineff(n, r)
        )
    m.addCons(sp.quicksum(lam[j] for j in J) == 1)

    for j in J:
        m.addCons(
            sp.quicksum(-ds.x_eff(j, i) * V[i] for i in I)
            + sp.quicksum(ds.y_eff(j, r) * U[r] for r in R)
            + h0 + k[j] == 0
        )
    for j in J:
        m.addConsSOS1([lam[j], k[j]])

    for i in I:
        xi = ds.x_ineff(n, i)
        m.addCons(d[i] * xi == s_m[i])
    for r in R:
        yr = ds.y_ineff(n, r)
        m.addCons(d[ds.n_inputs + r] * yr == s_p[r])

    m.addCons(sp.quicksum(d[v] for v in range(NV)) == NV * d_prom)

    obj = sp.quicksum((d[v] - d_prom) * (d[v] - d_prom) for v in range(NV))
    m.setObjective(obj, "minimize")
    m.optimize()

    if m.getStatus() == "optimal":
        vals: dict = {"d_prom": m.getVal(d_prom)}
        for j in J:
            vals[f"lambda_{ds.dmu_efficient[j]}"] = m.getVal(lam[j])
        for i in I:
            vals[f"S_MENOS_{ds.inputs[i]}"] = m.getVal(s_m[i])
            vals[f"d_{ds.inputs[i]}"]        = m.getVal(d[i])
        for r in R:
            vals[f"S_MAS_{ds.outputs[r]}"]   = m.getVal(s_p[r])
            vals[f"d_{ds.outputs[r]}"]        = m.getVal(d[ds.n_inputs + r])
        return SolveResult(
            status="optimal", objective=m.getObjVal(),
            variables=vals, solver_used="scip"
        )
    else:
        return SolveResult(
            status="infeasible", solver_used="scip",
            message=f"SCIP status: {m.getStatus()}"
        )


def solve_dmesm(
    ds: DEADataset,
    n: int,
    solver: Optional[str] = None,
) -> SolveResult:
    """
    Solve the DMESM model for inefficient DMU index ``n``.

    Parameters
    ----------
    ds : DEADataset
    n : int
    solver : str, optional

    Returns
    -------
    SolveResult
    """
    s = (solver or DEFAULT_SOLVER).lower()
    if s == "gurobi":
        return _solve_dmesm_gurobi(ds, n)
    elif s == "scip":
        return _solve_dmesm_scip(ds, n)
    else:
        raise ValueError(f"Unknown solver '{s}'. Choose from: {['gurobi','scip']}")


def run_dmesm(
    ds: DEADataset,
    solver: Optional[str] = None,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Run DMESM for all inefficient DMUs and return a results DataFrame.
    """
    report = ds.data_ineff.copy()

    for n in range(ds.n_ineff):
        dmu_name = ds.dmu_inefficient[n]
        result = solve_dmesm(ds, n, solver=solver)

        if not result.is_optimal:
            if verbose:
                print(f"  [DMESM] {dmu_name}: {result.status} — {result.message}")
            continue

        if verbose:
            print(f"  [DMESM] {dmu_name}: Var(d) = {result.objective:.6f}")

        report.loc[n, "Obj Value (Var_d)"] = result.objective

        for dmu in ds.dmu_efficient:
            report.loc[n, f"lambda_{dmu}"] = result.get(f"lambda_{dmu}")
        for inp in ds.inputs:
            report.loc[n, f"S_MENOS_{inp}"] = result.get(f"S_MENOS_{inp}")
            report.loc[n, f"d_{inp}"]        = result.get(f"d_{inp}")
        for out in ds.outputs:
            report.loc[n, f"S_MAS_{out}"]    = result.get(f"S_MAS_{out}")
            report.loc[n, f"d_{out}"]         = result.get(f"d_{out}")

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
        report.loc[n, "d_prom"]     = result.get("d_prom")

    return report
