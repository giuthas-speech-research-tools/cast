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
import multiprocessing as mp
from pathlib import Path

import numpy as np
import scipy.io.wavfile as sio_wavfile
from textgrids import TextGrid, Tier
from tqdm import tqdm

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


def split_tier_to_n(
        original: Path, new_file: Path, tier_name: str, new_names: list[str]
) -> None:
    """

    Parameters
    ----------
    original : Path
        Path to the original TextGrid.
    new_file : Path
        Path to the new TextGrid.
    tier_name : str
        Name of the Tier to split.
    new_names : list[str]
        Names of the new Tiers.
    """
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
        original: Path, new_file: Path, tier_name: str) -> None:
    """

    Parameters
    ----------
    original : Path
        Path to the original TextGrid.
    new_file : Path
        Path to the new TextGrid.
    tier_name : str
        Tier containing the beeps. This Tier should not contain any other
        boundaries.
    """
    wav_name = original.with_suffix(".wav")
    (sampling_frequency, frames) = sio_wavfile.read(wav_name)
    time = np.linspace(
        start=0,
        stop=float(len(frames[:, 0])) / sampling_frequency,
        num=len(frames[:, 0])
    )

    textgrid = TextGrid(original)
    tier = textgrid[tier_name]

    high_pass_filter = high_pass(sampling_frequency, 60)
    band_pass_filter = band_pass(sampling_frequency)

    new_boundaries = [
        interval.xmax for interval in tier
    ]

    # apply_args = [
    #     (add_sil, args, filenames, m_I, m_name, model_names,
    #     overwrite, quiet, use_ensemble, use_interp, word2phone)
    #     for m_I, m_name in enumerate(model_names, start=1)
    # ]
    # with mp.Pool() as pool:
    #     pool.starmap(apply_model, apply_args)
    #
    # for i, interval in enumerate(tqdm(tier[1:])):
    #     find_beep_in_slice(band_pass_filter, frames, high_pass_filter, i,
    #                        interval, new_boundaries, sampling_frequency, tier,
    #                        time, wav_name)

    for i, interval in enumerate(tqdm(tier)):
        if i == 0:
            continue

        if i == len(tier) - 1:
            max_index = len(frames) - 1
        else:
            max_index = np.where(time > interval.xmax)[0][0]
        min_index = np.where(time > interval.xmin)[0][0]
        interval_frames = frames[min_index:max_index, 1]

        beep_time, has_speech = detect_beep_and_speech(
            frames=interval_frames,
            sampling_frequency=sampling_frequency,
            b=high_pass_filter['b'],
            a=high_pass_filter['a'],
            name=str(wav_name),
            sos=band_pass_filter
        )
        new_boundaries[i] = interval.xmin + beep_time

    for i, boundary in enumerate(new_boundaries):
        if i == 0:
            continue
        tier[i].xmin = boundary
        tier[i-1].xmax = boundary

    textgrid.write(filename=new_file)


def find_beep_in_slice(
        band_pass_filter, frames, high_pass_filter, i, interval, new_boundaries,
        sampling_frequency, tier, time, wav_name
):
    if i == len(tier) - 1:
        max_index = len(frames) - 1
    else:
        max_index = np.where(time > interval.xmax)[0][0]
    min_index = np.where(time > interval.xmin)[0][0]
    interval_frames = frames[min_index:max_index, 1]
    beep_time, has_speech = detect_beep_and_speech(
        frames=interval_frames,
        sampling_frequency=sampling_frequency,
        b=high_pass_filter['b'],
        a=high_pass_filter['a'],
        name=str(wav_name),
        sos=band_pass_filter
    )
    new_boundaries[i] = interval.xmin + beep_time
