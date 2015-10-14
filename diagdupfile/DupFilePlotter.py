import DupFile

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

class DupFilePlotter(object):

    def __init__(self):
        pass

    def plot(self, dupfile_obj, filename):
        array_plot = dupfile_obj.per_tile_stats
        array_plot['side'] = array_plot['tile'].apply(lambda x: int(x/1000))
        array_plot['swath'] = array_plot['tile'].apply(lambda x: int(x % 1000 / 100))
        array_plot['tile'] = array_plot['tile'] % 100

        array_plot = array_plot.assign(dup_rate = array_plot['duplicate_count'] / (array_plot['unique_count'] + array_plot['duplicate_count']))
        pivot = pd.pivot_table(array_plot, index=['flowcell', 'lane', 'side', 'tile', 'subtile_y', 'swath', 'subtile_x'], values=['dup_rate']).unstack('swath').unstack('subtile_x')

        flowcells = pivot.index.get_level_values('flowcell').unique()
        lanes = pivot.index.get_level_values('lane').unique()
        sides = pivot.index.get_level_values('side').unique()
        assert(len(flowcells) == 1)

        pcdict = { 'red': ((0.0,239.0/255,239.0/255),
                           (1.0,63.0/255,63.0/255)),
                 'green': ((0.0,237.0/255,237.0/255),
                           (1.0,0.0,0.0)),
                  'blue': ((0.0,245.0/255,245.0/255),
                          (1.0,125.0/255,125.0/255))
                 }

        purples = LinearSegmentedColormap('PurplesDF', pcdict)

        figure, axes = plt.subplots(len(sides), len(lanes), figsize=(11, 8.5), dpi=300, squeeze=False)
        figure.suptitle("Per-tile duplication for flow cell " + flowcells[0])

        for row in range(len(sides)):
            for col in range(len(lanes)):
                axes[row][col].get_xaxis().set_visible(False)
                axes[row][col].get_yaxis().set_visible(False)
                if row == 0:
                    axes[row][col].set_title("Lane " + str(col+1))
                if col == 0:
                    yax = axes[row][col].get_yaxis()
                    axes[row][col].set_ylabel("Side " + str(row + 1))
                    yax.set_visible(True)
                    yax.set_ticks([])
            
                img_for_plot = pivot.loc[flowcells[0],lanes[col],sides[row]].as_matrix()
                imgplot = axes[row][col].imshow(img_for_plot,aspect='auto',cmap=purples, interpolation='quadric')
        
        figure.subplots_adjust(bottom=0.15, hspace=0.025, wspace=0.025)
        colorbar_ax = figure.add_axes([0.3, 0.12, 0.4, 0.02], aspect='auto')
        cbar = figure.colorbar(imgplot, cax=colorbar_ax, orientation='horizontal')
        cbar.set_label('Duplicate Rate')
        plt.savefig(filename, bbox_inches='tight')
