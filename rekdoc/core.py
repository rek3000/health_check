import click
from rekdoc import fetch as rekfetch
from rekdoc import doc as rekdoc
from rekdoc import tools 
from rekdoc.const import *

##### CORE #####
# @click.version_option(version='1.0.0', prog_name='rekdoc', message='created by Rek.')
@click.group()
def cli():
    pass
@click.command()
@click.option('-i', '--input', help='node names file.', type=click.File('r'))
@click.option('-o', '--output', required=True, help='output file name.')
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.option('-f', '--force', default=False, help='Force replace if exist output file.', is_flag=True)
@click.argument('node', required=False, nargs=-1)
def fetch(input, output, node, verbose, force):
    nodes = []
    try:
        for line in input:
            nodes.append(line.strip())
        if node:
            nodes.append(node)
    except:
        print()

    if rekfetch.run(nodes, output, verbose, force) == -1:
        rekfetch.clean_up_force()
        return -1
    click.secho('Summary file created after fetch: ' + output, fg='cyan')
    rekfetch.clean_up()

@click.command()
@click.option('-i', '--input', help='summary file.')
@click.option('-o', '--output', help='output file name.', type=click.STRING)
@click.option('-v', '--verbose', default=False, is_flag=True)
@click.option('-f', '--force', default=False, help='Force replace if exist output file.', is_flag=True)
def doc(input, output, verbose, force):
    if output == None:
        output = input
    rekdoc.run(input, output, verbose, force)

cli.add_command(fetch)
cli.add_command(doc)

if __name__ == '__main__':
    cli()
##### END CORE #####
