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
import pprint
from copy import deepcopy
from pathlib import Path

import numpy as np
import scipy.io.wavfile as sio_wavfile
from textgrids import TextGrid, Tier
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

from .audio_processing import band_pass, detect_beep_and_speech, high_pass

pp = pprint.PrettyPrinter(indent=4)


def delete_interval(
    tier: Tier,
    index: int,
    shift_right: bool = True,
) -> None:
    """
    Delete an Interval from a TextGrid Tier.

    The label of the Interval is discarded and the end time (xmax) of the
    previous Interval is set to the end time of the Interval to be deleted.

    Parameters
    ----------
    tier : Tier
        The Tier containing the Interval to be deleted.
    index : int
        Index of the Interval to be deleted.
    shift_right : bool
        Which way to shift the remaining intervals when deleting this one.
    """
    if shift_right:
        if index-1 >= 0:
            tier[index-1].xmax = tier[index].xmax
    else:
        if index+1 < len(tier):
            tier[index+1].xmin = tier[index].xmin
    del tier[index]


def remove_empty_intervals_from_grid(
        original_gridfile: Path,
        output_dir: Path
) -> None:
    """
    Delete all empty Intervals (expect first and last) in every Tier.

    Any empty segments apart from the first and last Interval of each Tier get
    deleted by extending the previous Interval to cover the deleted Interval's
    time span.

    The resulting new TextGrid is written with using the original name into the
    output directory.

    Parameters
    ----------
    original_gridfile : Path
        Path to the TextGrid file.
    output_dir : Path
        Path to the output directory.
    """
    if not original_gridfile.exists():
        print("Error: Original TextGrid file - " +
              str(original_gridfile) + " - does not exist.")

    if not output_dir.exists():
        output_dir.mkdir()

    grid = TextGrid(original_gridfile)
    for tier in grid:
        deletion_list = []
        for i, interval in enumerate(grid[tier][1:-1]):
            if not interval.text:
                deletion_list.append(i+1)
        deletion_list.reverse()
        for i in deletion_list:
            delete_interval(grid[tier], i)
    output_path = output_dir/original_gridfile.name
    grid.write(output_path)


def remove_empty_intervals_from_textgrids(
        original_dir: Path, 
        output_dir: Path,
) -> None:
    """
    Remove empty intervals from all TextGrids in the given directory.

    Parameters
    ----------
    original_dir : Path
        Path to directory which contains the original TextGrids.
    output_dir : Path
        Path to the output directory.
    """
    if not original_dir.exists():
        print("Fatal: Directory of original TextGrids does not exist.")
        exit()

    if not output_dir.exists():
        output_dir.mkdir()

    for textgrid in original_dir.glob("*.TextGrid"):
        remove_empty_intervals_from_grid(textgrid, output_dir)


def split_tier_in_two(
        original: Path,
        tier_name: str,
        new_names: list[str],
        new_file: Path | None = None
) -> None:
    """
    Split a TextGrid Tier into two Tiers.

    This is done by moving odd and even boundaries to separate Tiers.

    Parameters
    ----------
    original : Path
        Path to the original TextGrid.
    tier_name : str
        Name of the Tier to split.
    new_names : list[str]
        Names of the new Tiers.
    new_file : Path | None
        Path to the new TextGrid, by default None. If this is None, `_split` is
        added to the name of the original file to generate the name of the new
        file.
    """
    if new_file is None:
        new_name = original.stem + "_split.TextGrid"
        new_file = original.with_name(new_name)
    textgrid = TextGrid(original)
    tier = textgrid.pop(tier_name)
    for i, name in enumerate(new_names):
        textgrid[name] = deepcopy(tier)
        for j in range(len(textgrid[name])-2, -1, -1):
            if (j + i + 1) % len(new_names) == 0:
                delete_interval(textgrid[name], j, shift_right=False)

    prev = ""
    tier = textgrid[new_names[1]]
    for i in range(len(tier)):
        current = tier[i].text
        tier[i].text = prev
        prev = current
    textgrid.write(filename=new_file)


def align_beeps_in_textgrid(
        original: Path,
        tier_name: str,
        new_file: Path | None = None,
        wav_file: Path | None = None
) -> None:
    """
    Align rough beep boundaries accurately.

    The algorithm looks only at the first second following the manual boundary.
    The search will fail if the beep is before the manual boundary or if it more
    than a second after the manual boundary.

    Parameters
    ----------
    original : Path
        Path to the original TextGrid.
    tier_name : str
        Tier containing the beeps. This Tier should not contain any other
        boundaries.
    new_file : Path | None
        Path to the new TextGrid, by default None. If this is None, `_beeps' is
        added to the name of the original file to generate the name of the new
        file.
    wav_file : Path | None
        Path to the wav file corresponding to the TextGrid, by default None. If
        this is None, the name is formed by replacing `.TextGrid` in the
        TextGrid's name with `.wav`.
    """
    if new_file is None:
        new_name = original.stem + "_beeps.TextGrid"
        new_file = original.with_name(new_name)
    if wav_file is None:
        wav_name = str(original.with_suffix(".wav"))
    else:
        wav_name = str(wav_file)
    (sampling_frequency, frames) = sio_wavfile.read(wav_name)

    textgrid = TextGrid(original)
    tier = textgrid[tier_name]

    high_pass_filter = high_pass(sampling_frequency, 60)
    band_pass_filter = band_pass(
        sampling_frequency=sampling_frequency, low=980.0, high=1020.0)

    old_boundaries = [
        interval.xmax for interval in tier
    ]

    apply_args = [
        _make_beep_finding_arguments_constant_slice(
            band_pass_filter, frames, high_pass_filter,
            i, interval, old_boundaries, sampling_frequency,
            wav_name)
        for i, interval in enumerate(tier[:-1])
    ]

    new_boundaries = process_map(
        _find_beep_in_slice, apply_args, desc="Finding beeps")

    for i, boundary in enumerate(new_boundaries):
        tier[i].xmax = boundary
        tier[i+1].xmin = boundary

    textgrid.write(filename=new_file)


def _make_beep_finding_arguments_constant_slice(
        band_pass_filter, frames, high_pass_filter, i, interval,
        old_boundaries, sampling_frequency, wav_name
) -> dict:
    min_index = int(interval.xmax*sampling_frequency)
    max_index = min_index + 3*sampling_frequency
    if max_index > len(frames):
        max_index = len(frames)

    return {
            'band_pass_filter': band_pass_filter,
            'high_pass_filter': high_pass_filter,
            'index': i,
            'interval_frames': frames[min_index:max_index, 1],
            'sampling_frequency': sampling_frequency,
            'wav_name': wav_name,
            'old_boundary': old_boundaries[i],
        }


def _find_beep_in_slice(
        params: dict
) -> float:
    beep_time, has_speech = detect_beep_and_speech(
        frames=params['interval_frames'],
        sampling_frequency=params['sampling_frequency'],
        b=params['high_pass_filter']['b'],
        a=params['high_pass_filter']['a'],
        name=params['wav_name'],
        sos=params['band_pass_filter']
    )
    return params['old_boundary'] + beep_time


