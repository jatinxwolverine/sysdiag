import argparse
import json
import sys
from sysdiag.inspector import get_diagnostics

def render_human_report(data):
    lines = [
        "==============================",
        "  MACHINE DIAGNOSTICS REPORT  ",
        "==============================",
        f"Python Version: {data['python']['version']} ({'OK' if data['python']['is_healthy'] else 'Outdated'})",
        f"Disk Space:     {data['disk']['free_gb']} GB free out of {data['disk']['total_gb']} GB",
        f"Disk Alert:     {'WARNING: Low Disk' if data['disk']['is_low'] else 'Healthy'}",
        "\nEnvironment Variables:",
        f"  PATH: {data['environment']['PATH']}",
        f"  USER: {data['environment']['USER']}",
        "\nDeveloper Tools:"
    ]
    for tool, status in data["tools"].items():
        state = f"Installed ({status['path']})" if status["installed"] else "NOT FOUND"
        lines.append(f"  - {tool:8}: {state}")
    lines.append("==============================")
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Packaged CLI Diagnostics Tool")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output")
    parser.add_argument("--config", type=str, default=None, help="Path to optional config file")
    args = parser.parse_args()

    try:
        data = get_diagnostics(config_path=args.config)
    except (FileNotFoundError, ValueError) as err:
        sys.stderr.write(f"Error: {err}\n")
        sys.exit(2)  # Critical configuration failure

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(render_human_report(data))

    # Exit code logic:
    # 0 = All clear
    # 1 = Missing developer tools or warning
    if data["missing_tools"] or data["disk"]["is_low"]:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()