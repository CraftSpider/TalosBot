
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
        print("Usage: python3 runner.py <talos program>")
        exit(0)
    item = args[0]
    sys.argv = sys.argv[0:1] + sys.argv[2:]
    if item in name_folder.keys():
        talos = importlib.import_module(name_folder[item])
        result = talos.main()
        exit(result)
    else:
        print("Unrecognized program")
        exit(1)


if __name__ == "__main__":
    main()
