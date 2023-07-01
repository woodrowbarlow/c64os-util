#!/bin/env python
import argparse
import os
import sys
import c64os_util
from importlib import metadata


def create(args):
    print(args)


def append(args):
    print(args)


def extract(args):
    print(args)


def merge(args):
    print(args)


def ls(args):
    print(args)


def info(args):
    print(args)


def main():
    parser = argparse.ArgumentParser(
        description="an archiving utility for C64 OS",
        epilog="run '%(prog)s <subcommand> -h' for more information",
    )
    parser._optionals.title = "global options"
    subparsers = parser.add_subparsers(title="subcommands", metavar="")

    subparser = subparsers.add_parser(
        "create", aliases=["c"], help="create a new archive"
    )
    subparser.add_argument(
        "file",
        type=str,
        nargs="+",
        help="path to file or directory to be added to archive",
    )
    subparser.add_argument(
        "-o",
        "--output",
        type=str,
        help="write output to specified file (instead of stdout)",
    )
    subparser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.name.lower() for t in c64os_util.CarArchiveType],
        help="set the archive type (default: general)",
    )
    subparser.add_argument("--note", type=str, help="set the archive note field")
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--seq",
        dest="file_type",
        action="store_const",
        const=c64os_util.CarRecordType.SEQFILE,
        help="add files using the SEQ type (default)",
    )
    group.add_argument(
        "-p",
        "--prg",
        dest="file_type",
        action="store_const",
        const=c64os_util.CarRecordType.PRGFILE,
        help="add files using the PRG type",
    )
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "--recursive",
        action="store_true",
        help="add directory contents recursively (default)",
    )
    group.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="do not add directory contents recursively",
    )
    subparser.add_argument(
        "--no-empty-dir", action="store_true", help="do not add empty directories"
    )
    subparser.add_argument(
        "--remove-files",
        action="store_true",
        help="remove files from disk after adding them to the archive",
    )
    subparser.add_argument(
        "--exclude",
        type=str,
        help="exclude files matching the provided glob-style wildcard pattern",
    )
    subparser.add_argument(
        "--sort",
        action="store_true",
        help="when creating an archive, sort directory and file entries according to their name",
    )
    subparser.set_defaults(
        func=create,
        type="general",
        note="",
        file_type=c64os_util.CarRecordType.SEQFILE,
        recursive=True,
        output=sys.stdout.buffer,
    )

    subparser = subparsers.add_parser(
        "apppend", aliases=["a"], help="append files to the end of an archive"
    )
    subparser.add_argument("archive", type=str, help="path to archive file")
    subparser.add_argument(
        "file",
        type=str,
        nargs="+",
        help="path to file or directory to be added to archive",
    )
    subparser.add_argument(
        "-o",
        "--output",
        type=str,
        help="write output to specified file (instead of stdout)",
    )
    subparser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.name.lower() for t in c64os_util.CarArchiveType],
        help="change the archive type",
    )
    subparser.add_argument("--note", type=str, help="change the archive note field")
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--seq",
        dest="file_type",
        action="store_const",
        const=c64os_util.CarRecordType.SEQFILE,
        help="add files using the SEQ type (default)",
    )
    group.add_argument(
        "-p",
        "--prg",
        dest="file_type",
        action="store_const",
        const=c64os_util.CarRecordType.PRGFILE,
        help="add files using the PRG type",
    )
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "--recursive",
        action="store_true",
        help="add directory contents recursively (default)",
    )
    group.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="do not add directory contents recursively",
    )
    subparser.add_argument(
        "--no-empty-dir", action="store_true", help="do not add empty directories"
    )
    subparser.add_argument(
        "--remove-files",
        action="store_true",
        help="remove files from disk after adding them to the archive",
    )
    subparser.add_argument(
        "--exclude",
        type=str,
        help="exclude files matching the provided glob-style wildcard pattern",
    )
    subparser.add_argument(
        "--sort",
        action="store_true",
        help="after appending, re-sort directory and file entries according to their name",
    )
    subparser.set_defaults(
        func=append,
        file_type=c64os_util.CarRecordType.SEQFILE,
        recursive=True,
        output=sys.stdout.buffer,
    )

    subparser = subparsers.add_parser(
        "extract", aliases=["e"], help="extract files from an archive"
    )
    subparser.add_argument("archive", type=str, nargs="+", help="path to archive file")
    subparser.add_argument(
        "-o",
        "--output",
        type=str,
        help="create files in the specified directory (instead of current directory)",
    )
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "--no-seq", action="store_true", help="do not extract files of type SEQ"
    )
    group.add_argument(
        "--no-prg", action="store_true", help="do not extract files of type PRG"
    )
    subparser.add_argument(
        "--no-empty-dir", action="store_true", help="do not create empty directories"
    )
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "-f", "--force", action="store_true", help="silently overwrite existing files"
    )
    group.add_argument(
        "-k", "--skip", action="store_true", help="silently skip over existing files"
    )
    subparser.set_defaults(func=extract, output=os.getcwd())

    subparser = subparsers.add_parser(
        "merge", aliases=["m"], help="merge multiple archives into one"
    )
    subparser.add_argument("archive", type=str, nargs="+", help="path to archive file")
    subparser.add_argument(
        "-o",
        "--output",
        type=str,
        help="write output to specified file (instead of stdout)",
    )
    subparser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.name.lower() for t in c64os_util.CarArchiveType],
        help="change the archive type",
    )
    subparser.add_argument("--note", type=str, help="change the archive note field.")
    subparser.add_argument(
        "--sort",
        action="store_true",
        help="after concatenating, re-sort directory and file entries according to their name",
    )
    subparser.set_defaults(func=merge, output=sys.stdout.buffer)

    subparser = subparsers.add_parser(
        "list", aliases=["l"], help="list the files and directories within an archive"
    )
    subparser.add_argument("archive", type=str, help="path to archive file")
    subparser.add_argument(
        "base",
        type=str,
        default="",
        help="base starting path within the archive (defaults to root)",
    )
    subparser.add_argument(
        "-n", "--depth", type=int, default=-1, help="limit list to n directories deep"
    )
    subparser.set_defaults(func=ls)

    subparser = subparsers.add_parser(
        "info", aliases=["i"], help="read or write metadata on an archive"
    )
    subparser.add_argument("archive", type=str, help="path to archive file")
    subparser.add_argument(
        "field",
        type=str,
        choices=["type", "note", "timestamp"],
        help="field to read from or write to",
    )
    subparser.add_argument(
        "value",
        type=str,
        nargs="?",
        default=None,
        help="new value to write (omit for read)",
    )
    subparser.set_defaults(func=info)

    version = metadata.version("c64os_util")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=version),
    )

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
