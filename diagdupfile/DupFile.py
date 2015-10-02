import pandas as pd
import json

class DupFile(object):

    def __init__(self, summary, distance, num_times_duplicated, insert_size, per_tile_stats):
        self.summary = summary
        self.distance = distance
        self.num_times_duplicated = num_times_duplicated
        self.insert_size = insert_size
        self.per_tile_stats = per_tile_stats

    def __init__(self, filename):
        with open(filename) as data_file:
            data = json.load(data_file)

        self.summary = pd.DataFrame(data=data['summary'])
        self.distance = pd.DataFrame(data=data['distance'])
        self.num_times_duplicated = pd.DataFrame(data=data['num_times_duplicated'])
        self.insert_size = pd.DataFrame(data=data['insert_size'])
        self.per_tile_stats = pd.DataFrame(data=data['per_tile_stats'])
    
    def merge(self, objects):
        files = list(objects)
        files.append(self)
        df = pd.concat( [x.per_tile_stats for x in files])
        df = df.groupby(['flowcell', 'lane', 'tile', 'subtile_x', 'subtile_y']).sum()
        self.per_tile_stats = df

        df = pd.concat( [x.distance for x in files])
        df = df.groupby(['intratile_distance']).sum()
        self.distance = df

        df = pd.concat( [x.num_times_duplicated for x in files])
        df = df.groupby(['num_duplicates']).sum()
        self.num_times_duplicated = df

        df = pd.concat( [x.insert_size for x in files])
        df = df.groupby(['insert_size']).sum()
        self.insert_size = df

        df = pd.concat( [x.summary for x in files])
        df = df.sum()
        df['dup_rate'] = df['total_duplicate_fragments'] / df['total_fragments']
        df['estimated_library_dup_rate'] = (df['total_duplicate_fragments'] - df['total_flowcell_duplicates']) / (df['total_fragments'] - df['total_flowcell_duplicates'])
        df['subtile_dup_rate_stdev'] = (self.per_tile_stats['duplicate_count'] / (self.per_tile_stats['unique_count'] + self.per_tile_stats['duplicate_count'])).std(ddof=0)
        self.summary = pd.DataFrame(df).transpose()
