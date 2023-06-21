import pprint
from pathlib import Path

from textgrids import TextGrid, Tier

pp = pprint.PrettyPrinter(indent=4)

def delete_interval(
    tier: Tier,
    index: int
    ):
    """
    Delete an Interval from a TextGrid Tier.

    The label of the Interval is discarded and the end time (xmax) of the
    previous Interval is set to the end time of the Interval to be deleted.

    Parameters
    ----------
    tier : Tier
        The Tier containing the Inteval to be deleted.
    index : int
        Index of the Interval to be deleted.
    """
    tier[index-1].xmax = tier[index].xmax
    del tier[index]

def remove_empty_intervals_from_grid(
        original_gridfile: Path,
        output_dir: Path
    ):
    """
    Delete all empty Intervals (excpet first and last) in every Tier.

    Any empty segments apart from the first and last Interval of each get
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
        print("Error: Original TextGrid file - " + str(original_gridfile) + " - does not exist.")

    if not output_dir.exists():
        output_dir.mkdir()

    grid = TextGrid(original_gridfile)
    for tier in grid:
        deletion_list =  []
        for i, segment in enumerate(tier[1:-1]):
            if not segment.label:
                deletion_list.append(i+1)
        deletion_list.reverse()
        for i in deletion_list:
            delete_interval(tier, i)
    output_path = output_dir/original_gridfile.name
    grid.write(output_path)

# TODO: change this into a generic filtering function which takes a list of
# filters to apply to each texgrid. 
def remove_empty_intervals_from_textgrids(
        original_dir: Path, 
        output_dir: Path,
    ):
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
