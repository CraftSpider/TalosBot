#! /usr/bin/env python3

import sys
import os
import pathlib
import importlib
import builtins


name_folder = {
    "discord": "discord_talos",
    "server": "website",
    "twitch": "twitch_talos"
}


def main():
    loc = pathlib.Path(sys.argv[0]).parent
    args = sys.argv[1:]

    if len(args) == 0:
        print("Usage: runner.py <talos program> [program flags...]")
        return 0
    item = args[0]
    if item not in name_folder:
        print("Unrecognized program. Valid programs are:")
        print(", ".join(name_folder.keys()))
        return 1

    # Do environment setup
    del sys.argv[1]
    for i in ("quit", "exit", "help", "copyright", "license", "credits"):
        delattr(builtins, i)
    os.chdir(loc)

    # Load and execute desired program
    module = name_folder[item]
    talos = importlib.import_module(module)
    return talos.main()


if __name__ == "__main__":
    sys.exit(main())
