import os
import pathlib
from importlib import metadata
from typing import List, Optional

from ..car import C64Archive
from .parser.car import car_parser


def validate_paths(base_dir: pathlib.Path, *paths: pathlib.Path):
    if not base_dir.is_dir():
        raise ValueError(f"Base directory {base_dir} does not exist.")
    for path in paths:
        if not path.exists():
            # TODO find better exceptions
            raise ValueError(f"Path {path} does not exist.")
        if not base_dir in path.parents:
            raise ValueError(
                f"Path {path} is not within the base directory '{base_dir}'."
            )


def is_empty_dir(path: pathlib.Path):
    if not path.is_dir():
        return False
    return not any(path.iterdir())


def create_manifest(
    *paths: pathlib.Path,
    recursive: bool = True,
    no_empty_dir: bool = False,
    base_prefix: Optional[pathlib.Path] = None,
    root_prefix: Optional[pathlib.Path] = None,
):
    if base_prefix is None:
        base_prefix = pathlib.Path(os.getcwd())
    validate_paths(base_prefix, *paths)
    new_paths: List[pathlib.Path] = list(paths)
    if recursive:
        for path in paths:
            if not path.is_dir():
                continue
            new_paths += path.rglob("*")
    if no_empty_dir:
        new_paths = [path for path in new_paths if not is_empty_dir(path)]
    archive_paths = [path.relative_to(base_prefix) for path in new_paths]
    if root_prefix is not None:
        archive_paths = [root_prefix / path for path in archive_paths]
    return dict(zip(new_paths, archive_paths))


def do_create(args):
    archive = C64Archive(
        archive_type=args.archive_type,
        note=args.archive_note,
    )
    base_prefix = pathlib.Path(args.base_dir)
    root_prefix = pathlib.Path(args.dir_prefix)
    manifest = create_manifest(
        args.files,
        recursive=args.recursive,
        no_empty_dir=args.no_empty_dir,
        base_prefix=base_prefix,
        root_prefix=root_prefix,
    )
    for local_path, archive_path in manifest.items():
        with open(local_path, "rb") as buffer:
            archive.touch(
                archive_path,
                file_type=args.file_type,
                create_directories=True,
                buffer=buffer,
            )


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


def car_main():
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
