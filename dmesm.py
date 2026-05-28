# -*- coding: utf-8 -*-
"""
dea_suite.data
--------------
Data loading, validation, and preparation utilities for DEA models.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import pandas as pd


@dataclass
class DEADataset:
    """
    Holds the parsed and validated DEA dataset.

    Attributes
    ----------
    dmu_efficient : List[str]       Names of efficient DMUs (reference set)
    dmu_inefficient : List[str]     Names of inefficient DMUs (to be projected)
    inputs : List[str]              Input variable names
    outputs : List[str]             Output variable names
    data_eff : pd.DataFrame         Rows for efficient DMUs (reset index)
    data_ineff : pd.DataFrame       Rows for inefficient DMUs (reset index)
    """
    dmu_efficient: List[str]
    dmu_inefficient: List[str]
    inputs: List[str]
    outputs: List[str]
    data_eff: pd.DataFrame
    data_ineff: pd.DataFrame

    @property
    def n_inputs(self) -> int:
        return len(self.inputs)

    @property
    def n_outputs(self) -> int:
        return len(self.outputs)

    @property
    def n_eff(self) -> int:
        return len(self.dmu_efficient)

    @property
    def n_ineff(self) -> int:
        return len(self.dmu_inefficient)

    def x_eff(self, j: int, i: int) -> float:
        """Input i of efficient DMU j."""
        return float(self.data_eff.iloc[j, i + 1])

    def y_eff(self, j: int, r: int) -> float:
        """Output r of efficient DMU j."""
        return float(self.data_eff.iloc[j, self.n_inputs + 1 + r])

    def x_ineff(self, n: int, i: int) -> float:
        """Input i of inefficient DMU n."""
        return float(self.data_ineff.iloc[n, i + 1])

    def y_ineff(self, n: int, r: int) -> float:
        """Output r of inefficient DMU n."""
        return float(self.data_ineff.iloc[n, self.n_inputs + 1 + r])


def load_dataset(
    filepath: str | Path,
    n_inputs: int,
    n_outputs: int,
    condition_col: str = "Condition",
    eff_label: str = "EFF",
    no_eff_label: str = "No EFF",
) -> DEADataset:
    """
    Load and validate a DEA dataset from an Excel file.

    Parameters
    ----------
    filepath : str or Path
        Path to the .xlsx file.
    n_inputs : int
        Number of input columns (must follow the DMU name column).
    n_outputs : int
        Number of output columns (must follow the input columns).
    condition_col : str
        Name of the column that marks efficient/inefficient DMUs.
    eff_label : str
        Label used in ``condition_col`` for efficient DMUs.
    no_eff_label : str
        Label used in ``condition_col`` for inefficient DMUs.

    Returns
    -------
    DEADataset

    Raises
    ------
    FileNotFoundError
        If the Excel file does not exist.
    ValueError
        If the dataset fails validation checks.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path.resolve()}")

    base = pd.read_excel(path)

    # --- Validate condition column ----------------------------------------
    if condition_col not in base.columns:
        raise ValueError(
            f"Column '{condition_col}' not found. "
            f"Available columns: {list(base.columns)}"
        )

    # --- Validate column count -------------------------------------------
    expected_cols = 1 + n_inputs + n_outputs + 1  # DMU + inputs + outputs + condition
    if len(base.columns) < expected_cols:
        raise ValueError(
            f"Dataset has {len(base.columns)} columns but "
            f"{expected_cols} are expected "
            f"(1 DMU name + {n_inputs} inputs + {n_outputs} outputs + 1 condition)."
        )

    lane = base[base[condition_col] == no_eff_label].reset_index(drop=True)
    lae  = base[base[condition_col] == eff_label].reset_index(drop=True)

    if len(lane) == 0:
        raise ValueError(f"No rows with '{no_eff_label}' in '{condition_col}'.")
    if len(lae) == 0:
        raise ValueError(f"No rows with '{eff_label}' in '{condition_col}'.")

    dmu_col = base.columns[0]
    all_cols = list(base.columns)
    inputs  = all_cols[1 : n_inputs + 1]
    outputs = all_cols[n_inputs + 1 : n_inputs + n_outputs + 1]

    # --- Validate positivity ---------------------------------------------
    for col in inputs + outputs:
        if (base[col] <= 0).any():
            raise ValueError(
                f"Column '{col}' contains non-positive values. "
                "DEA requires strictly positive inputs and outputs."
            )

    dmu_e  = list(lae[dmu_col])
    dmu_ne = list(lane[dmu_col])

    return DEADataset(
        dmu_efficient=dmu_e,
        dmu_inefficient=dmu_ne,
        inputs=inputs,
        outputs=outputs,
        data_eff=lae,
        data_ineff=lane,
    )
