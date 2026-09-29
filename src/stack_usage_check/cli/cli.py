from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional

from stack_usage_check import stack_usage_processor
from stack_usage_check.utils.logger import configure_logger
from stack_usage_check._version import __version__


def main(argv: Optional[List[str]] = None) -> int:
    """ Main function that parses CLI arguments and execute the corresponding command

    Args:
        argv (list[str]): list of arguments passed in via CLI

    Returns:
        The error status code returned by the command as integer
    """
    args = parse_command_line_args(argv)

    configure_logger(args.log_level)
    command = args.command
    return command(args)


def parse_command_line_args(argv: Optional[List[str]] = None) -> Namespace:
    """ Function that parses arguments passed via CLI using argparse.

    Args:
        argv (list[str]): list of arguments passed in via CLI.

    Returns:
        A populated :class:`Namespace` object.
    """
    parser = ArgumentParser(description="Generates a json report file of stack usage. "
                                        "Parses GCC stack usage and RTE mappings "
                                        "from build artifacts. "
                                        "It will then compare the values against the .map file which contains "
                                        "the Stack array allocation", fromfile_prefix_chars="@")

    parser.add_argument("--log-level",
                        choices=["critical", "error", "warning", "info", "debug"],
                        default="info",
                        help="The log level to configure logging with.")

    parser.add_argument("-V", "--version",
                        action="version",
                        version=f"%(prog)s {__version__}")

    command_subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

    generate_parser = command_subparsers.add_parser("generate", help="Generate stack usage json report.")
    generate_parser.set_defaults(command=generate)

    generate_parser.add_argument("-t", "--obj-dir", help="Specify the built objs directory",
                                 required=False, type=Path)
    generate_parser.add_argument("-m", "--map-file", help="Target map file",
                                 required=True, type=Path)
    generate_parser.add_argument("-r", "--rte-arxml", help="Specify RTE arxml file",
                                 required=False, type=Path)
    generate_parser.add_argument("-o", "--output", help="Specify output json file",
                                 required=False, type=Path)
    generate_parser.add_argument("-f", "--memory-threshold-limit", help="Custom memory limit. Default is .85 (85%%)",
                                 required=False, type=float)

    return parser.parse_args(args=argv)


def generate(args: Namespace) -> int:
    processor = stack_usage_processor.StackUsageProcessor(vars(args))
    processor.process_stack_usage_info()
    return 0
