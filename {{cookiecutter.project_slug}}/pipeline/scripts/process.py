"""Placeholder pipeline stage script — replace with your processing logic.

Called by the ``process`` stage in ``dvc.yaml``. Reads a CSV from ``--input``
and writes a result to ``--output``; adapt the logic to your use case.
"""

import argparse
from pathlib import Path


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description="Process input data.")
    parser.add_argument("--input", required=True, type=Path, help="Path to input CSV.")
    parser.add_argument("--output", required=True, type=Path, help="Path to output CSV.")
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)

    # TODO: replace with real processing logic
    args.output.write_text(args.input.read_text())


if __name__ == "__main__":
    main()
