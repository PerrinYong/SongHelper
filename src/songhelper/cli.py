from __future__ import annotations

import argparse
from pathlib import Path

from .capabilities import render_capabilities
from .project import ensure_workspace
from .workflows import render_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="songhelper", description="Song creation helper workspace"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("capabilities", help="Show supported capabilities")
    subparsers.add_parser("workflow", help="Show recommended songwriting workflow")

    init_parser = subparsers.add_parser(
        "init-workspace", help="Create standard workspace folders"
    )
    init_parser.add_argument("--root", default=".", help="Project root")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "capabilities":
        print(render_capabilities())
        return 0

    if args.command == "workflow":
        print(render_workflow())
        return 0

    if args.command == "init-workspace":
        root = Path(args.root).resolve()
        created = ensure_workspace(root)
        print("Workspace folders ensured:")
        for item in created:
            print(f"- {item}")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
