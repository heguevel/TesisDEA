# -*- coding: utf-8 -*-
"""
dea_suite.report
----------------
Excel report generation for DEA results.
"""

from __future__ import annotations
from pathlib import Path
import datetime as dt
import pandas as pd


def save_report(
    results: dict[str, pd.DataFrame],
    base_filename: str,
    output_dir: str | Path = ".",
    timestamp: bool = True,
) -> Path:
    """
    Save one or more result DataFrames to a multi-sheet Excel workbook.

    Parameters
    ----------
    results : dict[str, pd.DataFrame]
        Mapping of sheet name → DataFrame.
    base_filename : str
        Base name for the output file (without extension).
    output_dir : str or Path
        Directory where the file will be written.
    timestamp : bool
        Append today's date (DDMMYYYY) to the filename.

    Returns
    -------
    Path
        Full path of the written file.
    """
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"_{dt.datetime.today().strftime('%d%m%Y')}" if timestamp else ""
    out_path = out_dir / f"{base_filename}{suffix}.xlsx"

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        for sheet_name, df in results.items():
            safe_name = sheet_name[:31]  # Excel sheet name limit
            df.to_excel(writer, sheet_name=safe_name, index=False)

    return out_path
