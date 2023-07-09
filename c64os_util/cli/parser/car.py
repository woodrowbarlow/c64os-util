"""
Definitions related to the car CLI script.
"""

import argparse
import os
import sys

from ...car import CarArchiveType, CarRecordType


def _create_parser(subparsers):
    subparser = subparsers.add_parser(
        "create", aliases=["c"], help="create a new archive"
    )
    subparser.add_argument(
        "file",
        dest="files",
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
        choices=[t.name.lower() for t in CarArchiveType],
        help="set the archive type (default: general)",
    )
    subparser.add_argument("--note", type=str, help="set the archive note field")
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--seq",
        dest="file_type",
        action="store_const",
        const=CarRecordType.SEQFILE,
        help="add files using the SEQ type (default)",
    )
    group.add_argument(
        "-p",
        "--prg",
        dest="file_type",
        action="store_const",
        const=CarRecordType.PRGFILE,
        help="add files using the PRG type",
    )
    subparser.add_argument(
        "--base-dir",
        type=str,
        help="structure the archive starting at "
        "this local dir (instead of current directory)",
    )
    subparser.add_argument(
        "--dir-prefix",
        type=str,
        help="inside the archive, place all files at "
        "this path (instead of the root)",
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
        dest="excludes",
        type=str,
        nargs="*",
        help="exclude files matching the provided glob-style wildcard pattern",
    )
    subparser.add_argument(
        "--sort",
        action="store_true",
        help="when creating an archive, sort directory "
        "and file entries according to their name",
    )
    subparser.set_defaults(
        subcmd="create",
        type="general",
        note="",
        file_type=CarRecordType.SEQFILE,
        recursive=True,
        no_empty_dir=False,
        remove_files=False,
        excludes=[],
        sort=False,
    )


def _append_parser(subparsers):
    subparser = subparsers.add_parser(
        "apppend", aliases=["a"], help="append files to the end of an archive"
    )
    subparser.add_argument("archive", type=str, help="path to archive file")
    subparser.add_argument(
        "file",
        dest="files",
        type=str,
        nargs="+",
        help="path to file or directory to be added to archive",
    )
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "-o",
        "--output",
        type=str,
        help="write output to specified file (instead of stdout)",
    )
    group.add_argument(
        "-i",
        "--in-place",
        action="store_true",
        help="operate directly on the input file (instead of generating a new output)",
    )
    subparser.add_argument(
        "-t",
        "--type",
        type=str,
        choices=[t.name.lower() for t in CarArchiveType],
        help="change the archive type",
    )
    subparser.add_argument("--note", type=str, help="change the archive note field")
    group = subparser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--seq",
        dest="file_type",
        action="store_const",
        const=CarRecordType.SEQFILE,
        help="add files using the SEQ type (default)",
    )
    group.add_argument(
        "-p",
        "--prg",
        dest="file_type",
        action="store_const",
        const=CarRecordType.PRGFILE,
        help="add files using the PRG type",
    )
    subparser.add_argument(
        "--base-dir",
        type=str,
        help="structure the archive starting at "
        "this local dir (instead of current directory)",
    )
    subparser.add_argument(
        "--dir-prefix",
        type=str,
        help="inside the archive, place all files at "
        "this path (instead of the root)",
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
        help="after appending, re-sort directory and "
        "file entries according to their name",
    )
    subparser.set_defaults(
        subcmd="append",
        file_type=CarRecordType.SEQFILE,
        base_dir=os.getcwd(),
        recursive=True,
        output=sys.stdout.buffer,
    )


def _extract_parser(subparsers):
    subparser = subparsers.add_parser(
        "extract", aliases=["e"], help="extract files from an archive"
    )
    subparser.add_argument("archive", type=str, help="path to archive file")
    subparser.add_argument(
        "file",
        dest="files",
        type=str,
        nargs="*",
        help="specific path (within archive) to be extracted (optional)",
    )
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
    subparser.set_defaults(subcmd="extract", output=os.getcwd())


def _merge_parser(subparsers):
    subparser = subparsers.add_parser(
        "merge", aliases=["m"], help="merge multiple archives into one"
    )
    subparser.add_argument(
        "archive", dest="archives", type=str, nargs="+", help="path to archive file"
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
        choices=[t.name.lower() for t in CarArchiveType],
        help="change the archive type",
    )
    subparser.add_argument("--note", type=str, help="change the archive note field.")
    subparser.add_argument(
        "--sort",
        action="store_true",
        help="after concatenating, re-sort directory and "
        "file entries according to their name",
    )
    subparser.set_defaults(subcmd="merge", output=sys.stdout.buffer)


def _list_parser(subparsers):
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
    subparser.set_defaults(subcmd="list")


def _info_parser(subparsers):
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
    subparser.set_defaults(subcmd="info")


def car_parser():
    """
    Build and return an argparse parser for car operations.

    :return: An argparse parser object (pre-populated).
    """
    parser = argparse.ArgumentParser(
        description="an archiving utility for C64 OS",
        epilog="run '%(prog)s <subcommand> -h' for more information",
    )
    parser._optionals.title = "global options"  # pylint: disable=W0212
    subparsers = parser.add_subparsers(title="subcommands", metavar="")
    _create_parser(subparsers)
    _append_parser(subparsers)
    _extract_parser(subparsers)
    _merge_parser(subparsers)
    _list_parser(subparsers)
    _info_parser(subparsers)
    return parser
