import os
import csv
import time
import click
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def count_words(filepath):
    """
    Count the number of words in a file.

    If the file cannot be decoded with UTF-8 encoding, ignore the bad data and count the words in the rest of the file.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            words = text.split()
            return len(words)
    except UnicodeDecodeError:
        click.echo(f'Ignoring bad data in file {filepath}.')
        return 0

def count_words_recursive(dirpath, extensions):
    """
    Recursively count the number of words in all files with the given extensions in a directory.

    Returns a dictionary containing the word count for each subdirectory.
    """
    wordcounts = {}
    for root, dirs, files in os.walk(dirpath):
        subdir_wordcount = 0
        for file in files:
            try:
                _, ext = os.path.splitext(file)
                if ext in extensions:
                    filepath = os.path.join(root, file)
                    subdir_wordcount += count_words(filepath)
            except FileNotFoundError:
                click.echo(f'Skipping file {file} because it does not exist.')
        wordcounts[root] = subdir_wordcount
    return wordcounts


@click.group()
def cli():
    pass


@cli.command()
@click.argument('title', nargs=-1)
@click.option('--dir', default='/home/Dropbox/wiki/posts', help='The base directory for the post')
@click.option('--date', default=None, help='The date of the post in YYYY-MM-DD format')
def makepost(title, dir, date):
    """
    Create a new blog post template.

    The positional parameters represent the title of the post.

    Optional arguments:
    --dir: The base directory for the post (default is current directory).
    --date: The date of the post in YYYY-MM-DD format (default is today).
    """
    title_str = '_'.join(title)

    # Create the filename
    if date is None:
        date_str = time.strftime('%Y-%m-%d')
    else:
        date_str = date

    filename = date_str + '-' + ''.join(c for c in title_str if c.isalnum() or c == ' ') + '.md'
    filepath = os.path.join(dir, filename)

    # Check if file already exists
    if os.path.exists(filepath):
        click.echo(f'File {filepath} already exists.')
        return

    # Write contents to file
    contents = f"""---
type: post
status: publish
title: {title_str}
date: {date_str}
---

"""
    with open(filepath, 'w') as f:
        f.write(contents)

    click.echo(f'Created post template {filename} in {dir}.')


@cli.command()
@click.option('--dir', default='/home/Dropbox/wiki', help='The directory to search for text files')
@click.option('--logfile', default='/home/Dropbox/notes_wordcounts.log', help='The path to the logfile')
@click.option('--quiet', is_flag=True, help='Suppress console output')
def blogwc(dir, logfile, quiet):
    """
    Recursively count the number of words in all .txt and .md files in a directory.

    Optional arguments:
    --dir: The directory to search for text files (default is /home/Dropbox/wiki).
    --logfile: The path to the logfile (default is /home/Dropbox/notes_wordcounts.log).
    """
    extensions = ['.txt', '.md']
    wordcounts = count_words_recursive(dir, extensions)

    total_wordcount = 0
    for subdir, wordcount in wordcounts.items():
        total_wordcount += wordcount
        if not quiet:
            click.echo(f'{subdir}: {wordcount} words')

    if not quiet: click.echo(f'Total word count: {total_wordcount}')

    # Log the word count to the logfile
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(logfile, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, total_wordcount])

        if not quiet: click.echo(f'Logged word count to {logfile}.')


@cli.command()
@click.option('--dir', default='/home/Dropbox/wiki', help='The directory to search for text files')
@click.option('--logfile', default='/home/Dropbox/notes_wordcounts.log', help='The path to the logfile')
def bloghist(dir, logfile):
    """
    Show a graph of the word counts over time, from a log file.

    Optional arguments:
    --dir: The directory to search for text files (default is /home/Dropbox/wiki).
    --logfile: The path to the logfile (default is /home/Dropbox/notes_wordcounts.log).
    """
    # Check if the logfile exists
    if not os.path.exists(logfile):
        click.echo(f'Log file {logfile} not found.')
        return

    # Read the data from the logfile
    data = []
    with open(logfile, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            try:
                timestamp = datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S')
                wordcount = int(row[1])
                data.append((timestamp, wordcount))
            except (ValueError, IndexError):
                click.echo(f'Skipping corrupt data in row {reader.line_num} of {logfile}.')

    # Check if there is any data to plot
    if not data:
        click.echo(f'No valid data found in {logfile}.')
        return

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot_date([d[0] for d in data], [d[1] for d in data], '-')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.set_xlabel('Date')
    ax.set_ylabel('Word count')
    ax.set_title('Word count over time')
    plt.show()

if __name__ == '__main__':
    cli()
