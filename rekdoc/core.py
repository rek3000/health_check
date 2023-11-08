import os, sys
import click
from rekdoc import fetch as rekfetch
from rekdoc import doc as rekdoc
from rekdoc import tools
from rekdoc.const import *

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


##### CORE #####
@click.version_option(
    version="1.0.0", prog_name="rekdoc", message="Version %(version)s \nCrafted by Rek."
)
@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@click.command(
    no_args_is_help=True,
    short_help="fetch info to img",
)
@click.option("-i", "--input", help="node names file.", type=click.File("r"))
@click.option("-o", "--output", required=True, help="output file name.")
@click.option("-v", "--verbose", default=False, is_flag=True)
@click.option(
    "-f",
    "--force",
    default=False,
    help="Force replace if exist output file.",
    is_flag=True,
)
@click.argument("node", required=False, nargs=-1)
def fetch(input, output, node, verbose, force):
    """
    \b
    Fetch information to json and convert to images
    This command examine the 'sample/' folder for logs
    """
    nodes = []
    try:
        for line in input:
            nodes.append(line.strip())
    except:
        pass
    if node:
        nodes.extend(node)
    print(nodes)

    root = os.path.split(output)[0]
    if rekfetch.run(nodes, output, verbose, force) == -1:
        rekfetch.clean_up_force("./temp/")
        click.secho("Error found!", bg="red", fg="black")
        sys.stdout.write("\033[?25h")
        return -1

    click.secho("Summary file created after fetch: " + output, fg="cyan")
    rekfetch.clean_up(
        "./temp/",
        prompt="Remove "
        + click.style("temp/", fg="cyan")
        + click.style(" directory items?", fg="red"),
        verbose=verbose,
    )

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
@click.option("-o", "--output", help="output file name.", type=click.STRING)
@click.option("-v", "--verbose", default=False, is_flag=True)
@click.option(
    "-f",
    "--force",
    default=False,
    help="Force replace if exist output file.",
    is_flag=True,
)
def doc(input, output, verbose, force):
    """
    \b
    Generate report from JSON file
    Require to have a sample docx file with defined styling rules to generate the document
    """

    if output == None:
        output = input

    file_name = rekdoc.run(input, output, verbose, force)
    if file_name == -1:
        click.secho("Error found!", bg="red", fg="black")
        return -1

    click.secho("Created document file: " + click.style(file_name, fg="cyan"))
    click.secho("Finish!", bg="green", fg="black")
    sys.stdout.write("\033[?25h")


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
            \d. Header 4: 'baocao4'/
        2. List
            Bullet-list('-' symbol): 'Dash List'
        Note: Failing to define styles with this specific name leads to 
              docx file generated having no style at all!

    MANDATORY DIRECTORY:
        'sample/'

    CODING CONVENTION:
        1. Naming style: 
            /   type         |    rule           \\
            |constant        : must be UPPPERCASE|
            |normal variable : snake_case        |
            |function name   : snake_case        |
            \comment         : use '#'           /
    For more information, visit: https://peps.python.org/pep-0008
    """
    )


cli.add_command(fetch)
cli.add_command(doc)
cli.add_command(rule)

if __name__ == "__main__":
    cli()
##### END CORE #####
