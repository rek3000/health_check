import os
import sys
import logging
import click
from rekdoc import fetch as rekfetch
from rekdoc import doc as rekdoc
from rekdoc import push as rekpush

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


##### CORE #####
@click.version_option(
    version="1.0.0", prog_name="rekdoc", message="Version %(version)s \nCrafted by Rek."
)
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """
    \b
    rekdoc - fetch, analyze and pump information to other source.

    \b
    A toolset allows user to get useful information from logs file of servers,
    generate images from them, analyze them pump to a document docx file.
    Moreover, the data fetched could be pushed to a SQL server.

    There are 3 subcommands also known as modules (fetch, push, doc) for user
    to interact with the toolset.

    Use 'rekdoc rule' to show the rules that need to comply
    to interact successfully with the toolset.
    """
    pass


@click.command(
    no_args_is_help=True,
    short_help="get information",
)
@click.option("-i", "--input", help="node names file.", type=click.File("r"))
@click.option("-o", "--output", required=True, help="output file.")
@click.option("-v", "--verbose", "log", default=False, flag_value="VERBOSE")
@click.option("--debug", "log", default=False, flag_value="DEBUG")
@click.option(
    "--dryrun", default=False, is_flag=True, help="purge the temp folder fetch run"
)
@click.option(
    "-s",
    "--sample",
    help="sample folder.",
    type=click.Path(exists=True),
    default="./sample/",
)
@click.option(
    "-f",
    "--force",
    default=False,
    help="Force replace if exist output file.",
    is_flag=True,
)
@click.argument("node", required=False, nargs=-1)
def fetch(input, output, sample, node, log, force, dryrun):
    """
    \b
    Fetch information to json and convert to images
    This command examine the 'sample/' folder for logs
    """
    if log == "VERBOSE":
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    elif log == "DEBUG":
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.WARNING)
    nodes = []
    try:
        for line in input:
            nodes.append(line.strip())
    except Exception as err:
        print(err)

    if node:
        nodes.extend(node)
    print(nodes)
    if dryrun:
        rekfetch.clean_up(
            "./temp/",
            prompt="Remove "
            + click.style("temp/", fg="cyan")
            + click.style(" directory items?", fg="red"),
            force=True,
        )

    # root = os.path.split(output)[0]
    try:
        rekfetch.run(nodes, sample, output, force)
    except RuntimeError:
        rekfetch.clean_up_force("./temp/")
        # rekfetch.clean_up_force("./temp/")
        click.secho("Error found!", bg="red", fg="black")
        sys.stdout.write("\033[?25h")
        return -1

    click.secho("Summary file created after fetch: " + output, fg="cyan")

    click.secho("Finish!", bg="green", fg="black")
    click.echo("")
    sys.stdout.write("\033[?25h")


@click.command(no_args_is_help=True, short_help="create report")
@click.option(
    "-i",
    "--input",
    help="summary file.",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "-m",
    "--image",
    help="image root path.",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
)
@click.option(
    "-s",
    "--sample",
    help="sample file.",
    type=click.Path(exists=True),
    default="sample.docx",
)
@click.option("-o", "--output", help="output file.", type=click.STRING)
@click.option("-v", "--verbose", "log", default=False, flag_value="VERBOSE")
@click.option("--debug", "log", default=False, flag_value="DEBUG")
@click.option(
    "-f",
    "--force",
    default=False,
    help="Force replace if exist output file.",
    is_flag=True,
)
def doc(input, output, sample, image, log, force):
    """
    \b
    Generate report from JSON file
    Require to have a sample docx file with defined styling rules
    to generate the document

    If there is not sample docx specified, 'sample.docx'
    will be used as the argument
    If there is not image root directory, the root of the input file is used.

    """
    if log == "VERBOSE":
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
    elif log == "DEBUG":
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.WARNING)

    if output is None:
        output = input
    if image is None:
        images_root = os.path.split(input)[0]
    else:
        images_root = image

    file_name = rekdoc.run(input, output, sample, images_root, force)
    if file_name == -1:
        click.secho("Error found!", bg="red", fg="black")
        return -1

    click.secho("Created document file: " + click.style(file_name, fg="cyan"))
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


# @click.command(no_args_is_help=True, short_help="show rules")
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
cli.add_command(push)
cli.add_command(rule)

if __name__ == "__main__":
    cli()
##### END CORE #####
