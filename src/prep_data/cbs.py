import pandas as pd
import geopandas as gpd
import numpy as np
import os   

"""CBS data:
1) load CBS data based on the citypy city TODO: extent? coordinates? 
2) clean attributes
3) save as ...
"""

# if __name__ == "__main__":
#     main()

def load_cbs(cbs_data):
    # load cbs data
    cbs = gpd.read_file(cbs_data)
    return cbs

# data1 = "./data/cbs/cbs_vk500_2023_v1.gpkg"
# print(load_cbs(data1))

