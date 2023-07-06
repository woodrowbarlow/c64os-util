#!/bin/env python
from importlib import metadata

from c64os_util.cli import car_parser


def do_create(args):
    print(args)


def do_append(args):
    print(args)


def do_extract(args):
    print(args)


def do_merge(args):
    print(args)


def do_list(args):
    print(args)


def do_info(args):
    print(args)


def main():
    subcmds = {
        "create": do_create,
        "append": do_append,
        "extract": do_extract,
        "merge": do_merge,
        "list": do_list,
        "info": do_info,
    }
    parser = car_parser()
    version = metadata.version("c64os_util")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=version),
    )
    args = parser.parse_args()
    subcmd_fn = subcmds[args.subcmd]
    subcmd_fn(args)


if __name__ == "__main__":
    main()
