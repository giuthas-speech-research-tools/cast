
# import os
import glob
import json
from textgrid import *

directory = 'gridfiles'
pattern = '*.TextGrid'
files = glob.glob(os.path.join(directory,pattern))
textgrids = map(TextGridFromFile, files, files)

grids = []
for (i, grid) in enumerate(textgrids):
    grids.append({'name':grid.name})
    for (tier) in grid.tiers:
        if hasattr(tier, 'intervals'):
            for interval in tier.intervals:
                grids[i][interval.mark] = [interval.minTime, interval.maxTime]
        else:
            for point in tier.points:
                grids[i][point.mark] = point.time

#for grid in grids:
#    print(grid['name'], grid['Lac'])

with open(directory + '.TGjson', 'w') as tgjson:
    json.dump(grids, tgjson, sort_keys=True, indent=2, separators=(',', ': '))

