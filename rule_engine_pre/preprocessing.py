import numpy as np
from typing import Tuple
from rule_dataclass import RuleSet

# CityPy templates are NumPy arrays stored in NPZ files
# bldg classes stored in 2D grid
# street clusters stored in 2D grid
# city center stored in 2D grid (only one cell with value 1)
# 100m x 100m grid cells

BUILDING_CLASSES = {
    'apartment': 14,
    'detached': 17,
    'terraced': 22,
    'none': 99
}

BUILDING_CLASS_NAMES = {v: k for k, v in BUILDING_CLASSES.items()}

# zone ids for visualization
ZONE_IDS = {
    '0_1km': 0,
    '1_2km': 1,
    '2_5km': 2,
    'unknown': 99
}

class TemplateModifier:
    """
    Modify CityPy templates based on rules.
    
    1. load template NPZ file from citypy
    2. for each grid cell:
        a. calculuate distance to city center
        b. find which zone the cell sits in
        c. look up housing rule for the corresponding zone
        d. look up landuse rule for the corresponding zone
        e. sample building class based on probabilities
        f. assign building class to grid cell
    3. save modified template NPZ file
        
        """
    
    def __init__(self, rules: RuleSet, random_seed: int = 42):
        self.rules = rules
        # Create independent random generator for reproducibility
        self.rng = np.random.default_rng(random_seed)
        print(f"  Initialized with random seed: {random_seed}")

    def modify_template(
        self,
        input_path: str,
        output_path: str,
        cell_size: float = 100.0
    ) -> dict: # returns dict with statistics about the modification

        print(f"\n{'='*60}")
        print("PREPROCESSING: modify NPZ template")
        print('='*60)
        
        # 1. load template
        print(f"\n 1. Loading template from: {input_path}")
        data = np.load(input_path)

        building_grid = data['building_class'].copy()
        street_grid = data['cluster_street'].copy()
        city_center_grid = data['city_center']
        
        # zone grid for visualization
        zone_grid = np.full(building_grid.shape, 99, dtype=np.int32)  # 99 = unknown

        rows, cols = building_grid.shape
        print(f"   Grid size: {rows} x {cols} cells")
        print(f"   Cell size: {cell_size}m")
        print(f"   Coverage: {rows * cell_size/1000:.1f} x {cols * cell_size/1000:.1f} km")
        
        # 2. find city center position
        center_row, center_col = np.where(city_center_grid == 1)
        if len(center_row) > 0:
            center_x = center_col[0] * cell_size
            center_y = center_row[0] * cell_size
        else:
            # grid center if not marked with 1
            center_x = cols * cell_size / 2
            center_y = rows * cell_size / 2
        
        print(f"   City center: grid[{center_row[0] if len(center_row) > 0 else rows//2}, "
              f"{center_col[0] if len(center_col) > 0 else cols//2}]")
        print(f"   City center: ({center_x:.0f}, {center_y:.0f}) -> relative to grid origin (0,0)")
        
        # 3. modify each cell
        print(f"\n 2. Modifying grid cells based on zone rules...")
        
        stats = {
            'total_cells': rows * cols,
            'by_zone': {},
            'by_type': {},
            'by_zone_and_type': {}  # Track type distribution per zone
        }

        for row in range(rows):
            for col in range(cols):
                # calculate cell center position
                ### FIXME: check for better way to do this ‼️
                x = col * cell_size
                y = row * cell_size

                # calculate distance to city center
                distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)

                # find zone
                zone = self.rules.get_zone(distance)
                if zone is None:
                    building_grid[row, col] = BUILDING_CLASSES['none']
                    zone_grid[row, col] = ZONE_IDS['unknown']
                    continue
                
                # assign zone id to zone grid
                zone_grid[row, col] = ZONE_IDS.get(zone.name, 99)
                
                # get housing rule for this zone
                housing_rule = self.rules.get_housing_rule(zone.name)
                if housing_rule is None:
                    building_grid[row, col] = BUILDING_CLASSES['none']
                    continue
                
                # get landuse rule for this zone
                landuse_rule = self.rules.get_landuse_rule(zone.name)
                if landuse_rule is None:
                    building_grid[row, col] = BUILDING_CLASSES['none']
                    continue
                
                # decide if this cell is residential (probabilistic)
                is_residential = self.rng.random() < landuse_rule.residential_pct
                
                if not is_residential:
                    # cell is NOT residential (commercial/industrial/etc)
                    building_grid[row, col] = BUILDING_CLASSES['none']
                    building_type = 'none'
                else:
                    # cell IS residential -> sample housing type
                    building_type = self._sample_building_type(housing_rule)
                    building_class_id = BUILDING_CLASSES.get(building_type, 99)
                    building_grid[row, col] = building_class_id
                
                # update stats
                stats['by_zone'][zone.name] = stats['by_zone'].get(zone.name, 0) + 1
                stats['by_type'][building_type] = stats['by_type'].get(building_type, 0) + 1
                
                # Track type distribution per zone
                if zone.name not in stats['by_zone_and_type']:
                    stats['by_zone_and_type'][zone.name] = {}
                stats['by_zone_and_type'][zone.name][building_type] = \
                    stats['by_zone_and_type'][zone.name].get(building_type, 0) + 1
        
        # 4. save modified template (CityStackGen-compatible: only 3 arrays!)
        print(f"\n 3. Saving modified template to: {output_path}")
        np.savez(
            output_path, 
            building_class=building_grid, 
            cluster_street=street_grid, 
            city_center=city_center_grid)
        
        print(f"   ✓ Saved modified template")
        
        # 5. save zone grid separately for visualization
        zone_output = output_path.replace('.npz', '_zones.npz')
        np.savez(
            zone_output,
            zone_grid=zone_grid,
            city_center=city_center_grid)
        
        print(f"   ✓ Saved zone grid to: {zone_output}")   

        # print statistics
        self._print_statistics(stats)
        
        return stats
    
    def _sample_building_type(self, housing_rule) -> str:
        # sample bldg type based on rule probabilities
        types = ['apartment', 'detached', 'terraced']
        probabilities = [housing_rule.apartment_pct, housing_rule.detached_pct, housing_rule.terraced_pct]
        return self.rng.choice(types, p = probabilities)

    def _print_statistics(self, stats: dict):
        print(f"\n{'='*60}")
        print("PREPROCESSING: Statistics")
        print('='*60)
        
        total = stats['total_cells']
        
        print(f"\nTotal cells: {total}")
        
        print(f"\nCells by zone:")
        for zone, count in sorted(stats['by_zone'].items()):
            pct = (count / total) * 100
            print(f"  {zone:15s}: {count:5d} cells ({pct:5.1f}%)")
        
        print(f"\nCells by building type:")
        for btype, count in sorted(stats['by_type'].items()):
            pct = (count / total) * 100
            print(f"  {btype:15s}: {count:5d} cells ({pct:5.1f}%)")
        
        print(f"{'='*60}")