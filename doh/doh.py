import re
import os
from datetime import datetime
import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('title', nargs=-1)
@click.option('--dir', default='/home/Dropbox/wiki/posts', help='The base directory for the post')
@click.option('--date', default=None, help='The date of the post in YYYY-MM-DD format')
def post(title, dir, date):
    """
    Create a new blog post template.

    The positional parameter TITLE represents the title of the post.

    Optional arguments:
    --dir: The base directory for the post.
    --date: The date of the post in YYYY-MM-DD format (default is today).
    """
    title = ' '.join(title)

    # Create the filename
    if date is None:
        date_str = datetime.today().strftime('%Y-%m-%d')
    else:
        date_str = date

    filename = date_str + '-' + re.sub(r'\W+', '_', title.lower()) + '.md'
    filepath = os.path.join(dir, filename)

    # Check if file already exists
    if os.path.exists(filepath):
        click.echo(f'File {filepath} already exists.')
        return

    # Write contents to file
    contents = f"""---
type: post
status: publish
title: {title}
date: {date_str}
---
"""
    with open(filepath, 'w') as f:
        f.write(contents)

    click.echo(f'Created post template {filename} in {dir}.')


@cli.command()
def foo():
    """
    A dummy subcommand for testing.
    """
    click.echo('This is the "foo" subcommand.')


if __name__ == '__main__':
    cli()
