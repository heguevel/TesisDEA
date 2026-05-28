# -*- coding: utf-8 -*-
"""
dea_suite.ui.server
--------------------
Local web server that serves the DEA Suite UI and provides
API endpoints for file upload and solver detection.

Usage
-----
    python -m dea_suite.ui          # starts server on http://localhost:5000
    dea-suite                       # same, via console entry point
"""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path

# ── Optional imports ────────────────────────────────────────────────────────
try:
    from flask import Flask, jsonify, request, send_from_directory
    _has_flask = True
except ImportError:
    _has_flask = False

try:
    import pandas as pd
    _has_pandas = True
except ImportError:
    _has_pandas = False


STATIC_DIR = Path(__file__).parent / "static"


def create_app() -> "Flask":
    if not _has_flask:
        raise ImportError(
            "Flask is required to run the DEA Suite UI.\n"
            "Install it with:  pip install flask"
        )

    app = Flask(__name__, static_folder=str(STATIC_DIR))

    # ── Serve the SPA ──────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return send_from_directory(str(STATIC_DIR), "index.html")

    @app.route("/<path:filename>")
    def static_files(filename):
        return send_from_directory(str(STATIC_DIR), filename)

    # ── Solver detection ───────────────────────────────────────────────────
    @app.route("/api/solvers")
    def api_solvers():
        from dea_suite.solvers import available_solvers
        try:
            solvers = available_solvers()
        except Exception:
            solvers = []
        return jsonify({"solvers": solvers})

    # ── File upload + parse ────────────────────────────────────────────────
    @app.route("/api/upload", methods=["POST"])
    def api_upload():
        if not _has_pandas:
            return jsonify({"error": "pandas not installed"}), 500

        f = request.files.get("file")
        if not f:
            return jsonify({"error": "No file"}), 400

        fname = f.filename or ""
        ext   = fname.rsplit(".", 1)[-1].lower()

        try:
            if ext in ("xlsx", "xls"):
                df = pd.read_excel(io.BytesIO(f.read()))
            elif ext == "csv":
                content = f.read().decode("utf-8", errors="replace")
                sep = ";" if content.count(";") > content.count(",") else ","
                df  = pd.read_csv(io.StringIO(content), sep=sep)
            else:
                return jsonify({"error": f"Unsupported format: {ext}"}), 400

            # Replace NaN with empty string for JSON serialisation
            df = df.fillna("")

            headers    = list(df.columns)
            rows       = df.head(5).values.tolist()
            total_rows = len(df)

            # Sanitise: convert everything to string for the preview
            rows_str = [[str(v) for v in row] for row in rows]

            return jsonify({
                "headers":    headers,
                "rows":       rows_str,
                "total_rows": total_rows,
            })

        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    # ── Run analysis ──────────────────────────────────────────────────────
    @app.route("/api/run", methods=["POST"])
    def api_run():
        """
        Accepts JSON with the full configuration and runs the analysis
        server-side if the data file is accessible.
        Not required when using the generated script workflow.
        """
        data = request.get_json(silent=True) or {}
        return jsonify({"status": "ok", "message": "Use the generated script to run locally."})

    return app


def launch(host: str = "127.0.0.1", port: int = 5000, open_browser: bool = True) -> None:
    """
    Start the DEA Suite UI server and optionally open a browser tab.

    Parameters
    ----------
    host : str
    port : int
    open_browser : bool
    """
    app = create_app()

    url = f"http://{host}:{port}"
    print(f"\n{'='*50}")
    print(f"  DEA Suite UI  →  {url}")
    print(f"{'='*50}")
    print("  Presioná Ctrl+C para detener el servidor.\n")

    if open_browser:
        # Small delay so Flask is ready before the browser opens
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    app.run(host=host, port=port, debug=False, use_reloader=False)


def main() -> None:
    """Entry point for  dea-suite  console command."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="dea-suite",
        description="DEA Suite — interfaz web local"
    )
    parser.add_argument("--host",  default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port",  default=5000, type=int, help="Puerto (default: 5000)")
    parser.add_argument("--no-browser", action="store_true", help="No abrir navegador automáticamente")
    args = parser.parse_args()

    launch(host=args.host, port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
