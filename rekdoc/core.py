import os
import sys
import logging
from logging.handlers import RotatingFileHandler
# from logging import Logger
from logging import Formatter, getLogger
from pathlib import Path
import click
from dotenv import load_dotenv
from rekdoc import fetch as rekfetch
from rekdoc import doc as rekdoc
from rekdoc import push as rekpush

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
load_dotenv("env.conf")
DEFAULT_OUTPUT = os.environ.get("OUTPUT_DIR", "/var/rd/")
DEFAULT_INPUT = os.environ.get("INPUT_DIR", "./sample/")

logger = getLogger(__package__)
log_path = Path("./rd.log")
log_size = 10000000
log_numbackups = 1
handler = RotatingFileHandler(
    log_path,
    maxBytes=log_size,
    backupCount=log_numbackups,
)


# ------------------------------
# CORE
# ------------------------------


@click.version_option(
    version="1.0", prog_name="Rekdoc",
    message="%(prog)s:VERSION:%(version)s"
)
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    \b
    rekdoc - fetch, analyze and draw report document.

    \b
    A toolset allows user to get useful information from logs file of servers,
    generate images from them, analyze them pump to a document docx file.
    Data fetched could be easily integrated to SQL database.

    There are 2 subcommands also known as modules (fetch, doc) for user
    to interact with the toolset.

    Configuration: Editing 'env.conf' file or using options in each command.

    """
    pass

#   Use 'rd rule' to show the rules that need to comply
#   to interact successfully with the toolset.


@click.command(
    no_args_is_help=False,
    short_help="get information",
)
@click.option("-o", "--output", "out_dir",
              default=DEFAULT_OUTPUT,
              type=click.Path(exists=True, path_type=Path),
              help="output folder.")
@click.option("-v", "--verbose", "log", default=False, flag_value="VERBOSE")
@click.option("--debug", "log", default=False, flag_value="DEBUG")
@click.option(
    "--dryrun", default=False,
    is_flag=True, help="purge the temp folder fetch run"
)
@click.option(
    "-i",
    "--input",
    "logs_dir",
    help="select sample folder.",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    default=DEFAULT_INPUT,
)
@click.option(
    "-f",
    "--force",
    default=False,
    help="Force replace if exist output file.",
    is_flag=True,
)
def fetch(
        logs_dir: Path, out_dir: Path, log: str, force: bool, dryrun: bool
) -> None:
    """
    \b
    Fetch information to json and convert to images

    This command (module) examine the logs directory to get list of logs
    then unpack log files to get necessary information
    Logs directory can be specified with '-i/--input' option.

    Default Output Directory: /var/rd/<CustomName>/<CurrentTimeStamp>
    """
    formatter = Formatter("%(levelname)s:%(message)s")
    if log == "VERBOSE":
        logger.setLevel("INFO")
    elif log == "DEBUG":
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("WARNING")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    print("Logs directory: " + str(logs_dir))
    print("Output directory: " + str(out_dir))
    print("----------------------------")
    if dryrun:
        rekfetch.clean_up(
            "./temp/",
            prompt="Remove "
            + click.style("temp/", fg="cyan")
            + click.style(" directory items?", fg="red"),
            force=True,
        )

    try:
        out_file = rekfetch.run(logs_dir, out_dir, force)
    except RuntimeError as err:
        # rekfetch.clean_up_force("./temp/")
        # click.secho("Error found!", bg="red", fg="black")
        click.secho("Error found!" + err, bg="red", fg="black")
        sys.stdout.write("\033[?25h")
        sys.exit()

    click.secho("Data File Created: " + str(out_file), fg="cyan")

    click.secho("Finish!", bg="green", fg="black")
    click.echo("")
    sys.stdout.write("\033[?25h")


@click.command(no_args_is_help=True, short_help="create report")
@click.option(
    "-i",
    "--input",
    help="summary file.",
    type=click.Path(exists=True, file_okay=True,
                    dir_okay=False, readable=True,
                    path_type=Path),
)
@click.option(
    "-m",
    "--image",
    help="image root path.",
    type=click.Path(exists=True, file_okay=False,
                    dir_okay=True, path_type=Path),
)
@click.option(
    "-s",
    "--sample",
    help="sample file.",
    required=False,
    type=click.Path(path_type=Path),
    # type=click.Path(path_type=Path),
    default="sample.docx",
)
@click.option(
    "-sa",
    "--sample-appendix",
    help="appendix sample file.",
    # type=click.Path(exists=True, path_type=Path),
    type=click.Path(exists=True, file_okay=True,
                    dir_okay=False, readable=True,
                    path_type=Path),
    default="appendix-sample.docx",
)
@click.option("-o", "--output", help="output file.",
              type=click.Path(path_type=Path))
@click.option("-v", "--verbose", "log", default=False, flag_value="VERBOSE")
@click.option("--debug", "log", default=False, flag_value="DEBUG")
@click.option(
    "-f",
    "--force",
    default=False,
    help="Force replace if exist output file.",
    is_flag=True,
)
def doc(input, output, sample, sample_appendix, image, log, force):
    """
    \b
    Generate report from JSON file
    Require to have a sample docx file with defined styling rules
    to generate the document

    If there is not sample docx specified, 'sample.docx'
    will be used as the argument
    If there is not image root directory, the root of the input file is used.

    """
    formatter = Formatter("%(levelname)s:%(message)s")
    if log == "VERBOSE":
        logger.setLevel(logging.INFO)
    elif log == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if output is None:
        output = input
        # output = "output/"
    if image is None:
        # images_root = os.path.split(input)[0]
        images_root = input.parent
    else:
        images_root = image

    doc_names = rekdoc.run(input, output, sample,
                           sample_appendix, images_root, force)

    if doc_names == -1:
        click.secho("Error found!", bg="red", fg="black")
        sys.stdout.write("\033[?25h")
        return -1

    click.secho("CREATED REPORT FILE: " +
                click.style(doc_names, fg="cyan"))
    rekfetch.clean_up(
        "./temp/",
        prompt=click.style("REMOVE ", fg="red")
        + click.style("EXTRACTED LOGS?", fg="cyan")
        # + click.style(" items?", fg="red"),
    )
    click.secho("Finish!", bg="green", fg="black")
    sys.stdout.write("\033[?25h")


@click.command(no_args_is_help=True, short_help="push data to database")
@click.option("-i", "--input", required=True, help="data json file.")
def push(input):
    """
    \b
    Insert data to SQL database

    \b
    Environment Variables
    ---------------------
    This module works by specifying Environment Variables
    to connect to SQL server
    and insert data to database.
        - DB_HOST: specify host of the SQL server
        - DB_PORT: specify port which the SQL server is listening to
        - DB_USERNAME
        - DB_PASSWORD
        - DB_DATABASE: specify a database to work with
    Default Environment Value:
        {
            DB_HOST: '127.0.0.1',
            DB_PORT: '3306',
            DB_USERNAME: 'rekdoc',
            DB_PASSWORD: 'welcome1',
            DB_DATABASE: 'logs',
        }
    """
    rekpush.run(input)


@click.command(short_help="show rules")
def rule():
    click.echo(
        """
    DOCUMENT SAMPLE RULES (These must be defined on 'docx' office software):
        1. Header
            /   TYPE    |  NAME   \\
            |a. Header 1: 'baocao1'|
            |b. Header 2: 'baocao2'|
            |c. Header 3: 'baocao3'|
            \\d. Header 4: 'baocao4'/
        2. List
            Bullet-list('-' symbol): 'Dash List'
        Note: Failing to define styles with this specific name leads to
              docx file generated having no style at all!
    \b
    REQUIREMENT:
        - logs
        - a sample docx file to use 'doc' module

    CODING CONVENTION:
        1. Naming style:
            /   type         |    rule           \\
            |constant        : must be UPPPERCASE|
            |normal variable : snake_case        |
            |function name   : snake_case        |
            \\comment         : use '#'           /
    For more information, visit: https://peps.python.org/pep-0008
    """
    )


cli.add_command(fetch)
cli.add_command(doc)
# cli.add_command(push)
# cli.add_command(rule)

if __name__ == "__main__":
    cli()
# ------------------------------
# END CORE
# ------------------------------
