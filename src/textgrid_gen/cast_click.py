#
# Copyright (c) 2022-2024 Pertti Palo.
#
# This file is part of Computer Assisted Segmentation Tools
# (see https://github.com/giuthas-speech-research-tools/cast/).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# The example data packaged with this program is licensed under the
# Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License. You should have received a
# copy of the Creative Commons Attribution-NonCommercial-ShareAlike 4.0
# International (CC BY-NC-SA 4.0) License along with the data. If not,
# see <https://creativecommons.org/licenses/by-nc-sa/4.0/> for details.
#
# When using the toolkit for scientific publications, please cite the
# articles listed in README.markdown. They can also be found in
# citations.bib in BibTeX format.
#

"""
Command line argument parser.
"""
import sys
from pathlib import Path

import click
from icecream import ic

from .configuration import CastConfig
from .clean_textgrids import (
    align_beeps_in_textgrid, remove_empty_intervals_from_textgrids,
    split_tier_in_two
)
from .concatenate import concatenate_wavs
from .extract import extract_textgrids
from .textgrid_functions import add_tiers


@click.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False), )
@click.argument(
    "config_file",
    type=click.Path(exists=True, dir_okay=False, file_okay=True), )
def add(directory: str, config_file: str) -> None:
    """
    Add the next active Tier.

    \b
    DIRECTORY contains the TextGrids to process.
    CONFIG_FILE is the configuration .yaml file.
    """
    configuration = CastConfig(Path(config_file))
    pronunciation_dict = None
    add_tiers(path=directory,
              configuration=configuration.main_config,
              pronunciation_dict=pronunciation_dict)


@click.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False), )
@click.argument("config_file")
@click.option(
    '-a', '--add',
    type=click.Choice(['none', 'first', 'all'], case_sensitive=False))
def concatenate():
    """
    Concatenate TextGrids.

    \b
    DIRECTORY contains the .TextGrid files to process.
    CONFIG_FILE is the configuration .yaml file.

    NOT IMPLEMENTED YET.
    """
    pass
    # pronunciation_dict = None
    # concatenate_wavs(
    #     path, config, pronunciation_dict)


@click.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False), )
@click.argument("config_file")
@click.argument("tier")
def delete():
    """
    Delete a Tier from TextGrids.

    \b
    DIRECTORY contains the .wav files to process.
    CONFIG_FILE is the configuration .yaml file.
    TIER is the name of the tier to delete.

    NOT IMPLEMENTED YET.
    """
    pass


@click.command()
@click.argument(
    "textgrid",
    type=click.Path(exists=True, dir_okay=False, file_okay=True), )
@click.argument(
    "directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False), )
@click.argument("config_file")
def extract():
    """
    Extract individual TextGrids from a long one.

    \b
    TEXTGRID the long TextGrid.
    DIRECTORY to extract the TextGrids to.
    CONFIG_FILE is the configuration .yaml file.

    NOT IMPLEMENTED YET.
    """
    pass
    # extract_textgrids(Path(path), Path(config['outputfile']))


@click.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False), )
@click.argument("config_file")
@click.option(
    '-a', '--add',
    type=click.Choice(['none', 'first', 'all'], case_sensitive=False))
def init():
    """
    Create TextGrids for each .wav file. Optionally add Tiers.

    \b
    DIRECTORY contains the .wav files to process.
    CONFIG_FILE is the configuration .yaml file.

    NOT IMPLEMENTED YET.
    """
    # TODO: this is for creating empty TextGrids from wavs, or a list of begin
    # and end values, or just end values.


@click.command()
def remove_double_bounds():
    """
    Remove double boundaries between words.

    \b
    DIRECTORY contains the .wav files to process.
    CONFIG_FILE is the configuration .yaml file.

    NOT IMPLEMENTED YET.
    """
    pass
    # if not config['output_dirname']:
    #     print(
    #         'Fatal: No output directory for new textgrids specified in '
    #         'config file.')
    # remove_empty_intervals_from_textgrids(
    #     Path(path), Path(config['output_dirname']))


@click.command()
@click.argument(
    "directory",
    type=click.Path(exists=True, dir_okay=True, file_okay=False), )
@click.argument("config_file")
@click.argument("tier")
def scramble():
    """
    Scramble an existing Tier in TextGrids.

    \b
    DIRECTORY contains the .wav files to process.
    CONFIG_FILE is the configuration .yaml file.
    TIER is the name of the tier to scramble.

    NOT IMPLEMENTED YET.
    """
    pass


@click.command()
@click.argument(
    "original",
    type=click.Path(exists=True, dir_okay=True, file_okay=True), )
@click.argument("tier")
@click.argument("new-names")
@click.option(
    "-n", "--new-path",
    type=click.Path(dir_okay=True, file_okay=True), )
def split_tier(
    original: str,
    tier: str,
    new_names: str,
    new_path: str | None = None,
) -> None:
    """
    Split tier in TextGrid(s) into two Tiers.

    \b
    ORIGINAL Either a TextGrid or a directory containing TextGrids.
    TIER is the name of the Tier to split.
    NEW-PATH Either name or directory for the new TextGrid(s).
    NEW_NAMEs The names of the new Tiers. This should be exactly two names
        separated by a space.
    """
    original = Path(original)
    if new_path is None and original.is_dir():
        new_name = original.name + '_split'
        new_path = original.with_name(new_name)
    elif new_path is not None:
        new_path = Path(new_path)
    new_names = new_names.split(" ")
    if len(new_names) != 2:
        print(
            f"There should be exactly two names for new tiers. Instead found "
            f"{len(new_names)} in {' '.join(new_names)}."
        )
        sys.exit()

    files = []
    new_files = []
    if original.is_file():
        if original.suffix == '.TextGrid':
            files = [original]
            new_files = [new_path]
        else:
            # logger.fatal(
            print(
                f"Wrong file type passed. Expected .TextGrid or a"
                f"directory, found {original.suffix}.")
            sys.exit()
    else:
        if not new_path.is_dir():
            # logger.fatal(
            print(
                f"If ORIGINAL is a directory, NEW should also be a directory. "
                f"Instead got {new_path}, which is not a directory."
            )
            sys.exit()
        files = list(original.glob("*.TextGrid"))
        new_files = [new_path / file.name for file in files]

    for file, new_file in zip(files, new_files):
        split_tier_in_two(
            original=file,
            new_file=new_file,
            tier_name=tier,
            new_names=new_names)


@click.command()
@click.argument(
    "original",
    type=click.Path(exists=True, dir_okay=True, file_okay=True), )
@click.option(
    "-w", "--wav-file",
    type=click.Path(dir_okay=False, file_okay=True), )
@click.option(
    "-n", "--new-path",
    type=click.Path(dir_okay=True, file_okay=True), )
@click.option("-t", "--tier-name", type=str)
def align_beeps(
        original: str,
        wav_file: str | None = None,
        new_path: str | None = None,
        tier_name: str | None = 'beep'
) -> None:
    """
    Align beep boundaries in TextGrid(s).

    \b
    ORIGINAL Either a TextGrid or a directory containing TextGrids.
    NEW-PATH Either name or directory for the new TextGrid(s).
    WAV-FILE Name of the wavfile to use. Only used when ORIGINAL is a file.
    TIER-NAME The name of the Tier containing the guesses for beep boundaries.
        Defaults to 'beep'.
    """
    original = Path(original)
    if new_path is None and original.is_dir():
        new_name = original.name + '_beeps'
        new_path = original.with_name(new_name)
    elif new_path is not None:
        new_path = Path(new_path)

    if wav_file is not None and original.is_file():
        wav_file = Path(wav_file)
    else:
        wav_file = None

    files = []
    new_files = []
    if original.is_file():
        if original.suffix == '.TextGrid':
            files = [original]
            new_files = [new_path]
        else:
            # logger.fatal(
            print(
                f"Wrong file type passed. Expected .TextGrid or a"
                f"directory, found {original.suffix}.")
            sys.exit()
    else:
        if not new_path.is_dir():
            # logger.fatal(
            print(
                f"If ORIGINAL is a directory, NEW should also be a directory. "
                f"Instead got {new_path}, which is not a directory."
            )
            sys.exit()
        files = list(original.glob("*.TextGrid"))
        new_files = [new_path / file.name for file in files]

    for file, new_file in zip(files, new_files):
        align_beeps_in_textgrid(
            original=file,
            new_file=new_file,
            tier_name=tier_name,
            wav_file=wav_file,
        )
