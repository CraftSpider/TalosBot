#! /usr/bin/env python3

import sys
import importlib


name_folder = {
    "discord": "discord_talos",
    "server": "website",
    "twitch": "twitch_talos"
}


def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print("Usage: runner.py <talos program>")
        exit(0)
    item = args[0]
    sys.argv = sys.argv[0:1] + sys.argv[2:]
    if item in name_folder.keys():
        talos = importlib.import_module(name_folder[item])
        sys.exit(talos.main())
    else:
        print("Unrecognized program. Valid programs are:")
        print(", ".join(name_folder.keys()))
        exit(1)


if __name__ == "__main__":
    main()
