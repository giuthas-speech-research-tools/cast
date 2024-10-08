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
Main API of CAST - Computer Assisted Segmentation Tools
"""

from .audio_processing import high_pass, high_pass_50, detect_beep_and_speech
from .clean_textgrids import remove_empty_intervals_from_textgrids
from .cli import run_cli
from .concatenate import concatenate_wavs
from .configuration import (read_config_file, read_exclusion_list,
                            read_pronunciation_dict)
from .csv_output import write_results
from .extract import extract_textgrids
from .meta.aaa_meta import check_and_load_aaa_meta
from .meta.csv_meta import check_and_load_csv_meta
from .meta.rasl_meta import check_and_load_rasl_meta
from .textgrid_functions import (
    add_tiers, add_tiers_to_textgrid, generate_textgrid
)
