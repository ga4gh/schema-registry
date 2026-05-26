"""CLI entry point: python -m compliance <url> [--json] [--verbose]"""

import argparse
import json
import sys
from dataclasses import asdict

from compliance.compliance import run_compliance


def _print_table(report, verbose: bool) -> None:
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box

        console = Console()
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Status", width=6)
        table.add_column("Check", style="dim")
        table.add_column("ms", justify="right", width=8)
        table.add_column("Message")

        for result in report.results:
            if result["passed"]:
                status = "[green]PASS[/green]"
            elif result.get("recommended"):
                status = "[yellow]WARN[/yellow]"
            else:
                status = "[red]FAIL[/red]"
            msg = (result.get("error") or result.get("message") or "")[:80]
            if verbose or not result["passed"]:
                table.add_row(status, result["name"], f"{result['duration_ms']:.1f}", msg)

        console.print(f"\n[bold]Schema Registry Compliance Report[/bold]")
        console.print(f"Server: {report.server_url}")
        console.print(f"Time:   {report.timestamp}\n")
        console.print(table)
        summary = f"[bold]Results:[/bold] {report.passed}/{report.total} passed"
        if report.failed:
            summary += f", [red]{report.failed} required failed[/red]"
        if report.recommended_failed:
            summary += f", [yellow]{report.recommended_failed} recommended failed[/yellow]"
        console.print(summary)
    except ImportError:
        # Fallback without rich
        print(f"\nSchema Registry Compliance Report")
        print(f"Server: {report.server_url}")
        print(f"Time:   {report.timestamp}\n")
        for result in report.results:
            if result["passed"]:
                status = "PASS"
            elif result.get("recommended"):
                status = "WARN"
            else:
                status = "FAIL"
            if verbose or not result["passed"]:
                msg = (result.get("error") or result.get("message") or "")[:80]
                print(f"  [{status}] {result['name']}  {result['duration_ms']:.1f}ms  {msg}")
        summary = f"\nResults: {report.passed}/{report.total} passed"
        if report.failed:
            summary += f", {report.failed} required failed"
        if report.recommended_failed:
            summary += f", {report.recommended_failed} recommended failed"
        print(summary)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GA4GH Schema Registry compliance checker",
        prog="compliance",
    )
    parser.add_argument("url", help="Base URL of the schema registry server")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show all checks, not just failures")
    args = parser.parse_args()

    try:
        report = run_compliance(args.url)
    except Exception as e:
        print(f"Fatal error before any checks ran: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        _print_table(report, verbose=args.verbose)

    sys.exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    main()
