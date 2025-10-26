import pandas as pd
import geopandas as gpd
import sys
from pathlib import Path
from typing import Tuple

# add parent directory to path for imports
PARENT_DIR = Path(__file__).parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from postprocessing.building_processor import BuildingProcessor, load_buildings_from_geojson, get_city_center_from_geojson
from rules.parser import RuleParser


def postprocess_citystackgen_output(
    buildings_geojson: str,
    city_center_geojson: str,
    rules_yaml: str,
    output_geojson: str = None,
    output_csv: str = None,
    random_seed: int = 123
) -> gpd.GeoDataFrame:
    """
    Postprocess CityStackGen output with full statistics and printing
    
    Args:
        buildings_geojson: Path to buildings GeoJSON
        city_center_geojson: Path to city center GeoJSON
        rules_yaml: Path to rules YAML file
        output_geojson: Path to output GeoJSON (optional)
        output_csv: Path to output CSV (optional)
        random_seed: Random seed for reproducibility
        
    Returns:
        GeoDataFrame with processed buildings (classified with zones, types, households)
    """
    print(f"\n{'='*60}")
    print("POSTPROCESSING: classify buildings")
    print('='*60)
    
    # 1. load buildings
    print(f"\n[1] Loading buildings from: {buildings_geojson}")
    buildings_gdf = load_buildings_from_geojson(buildings_geojson)

    # 2. get city center
    print(f"\n[2] Getting city center from: {city_center_geojson}")
    city_center = get_city_center_from_geojson(city_center_geojson)

    # 3. load rules
    print(f"\n[3] Loading rules from: {rules_yaml}")
    parser = RuleParser()
    rules = parser.load_from_yaml(rules_yaml)
    print(f"  Loaded {len(rules.zones)} zones")
    print(f"  Loaded {len(rules.housing_rules)} housing rules")
    print(f"  Loaded {len(rules.household_rules)} household rules")
    print(f"  Loaded {len(rules.residents_rules)} residents rules")
    print(f"  Loaded {len(rules.unit_size_rules)} unit size rules")
    
    # 4. process buildings (includes household assignment)
    print(f"\n[4] Processing buildings...")
    processor = BuildingProcessor(rules, random_seed=random_seed)
    final_buildings = processor.process_buildings(buildings_gdf, city_center)
    
    # 5. save results
    if output_geojson:
        print(f"\n[5] Saving classified buildings to: {output_geojson}")
        final_buildings.to_file(output_geojson, driver='GeoJSON')
        print(f"  ✓ Saved {len(final_buildings)} buildings")
    
    if output_csv:
        print(f"\n[6] Saving building data to: {output_csv}")
        # Convert to regular DataFrame for CSV
        csv_data = final_buildings.drop(columns=['geometry', 'centroid'])
        csv_data.to_csv(output_csv, index=False)
        print(f"  ✓ Saved building data")
    
    # 6. print statistics
    print(f"\n[7] Postprocessing complete!")
    _print_postprocessing_statistics(final_buildings)
    
    return final_buildings


def _print_postprocessing_statistics(buildings_gdf: gpd.GeoDataFrame):
    """Print postprocessing statistics"""
    print(f"\n{'='*60}")
    print("POSTPROCESSING: Statistics")
    print('='*60)
    
    total = len(buildings_gdf)
    
    print(f"\nTotal buildings: {total}")
    
    if 'zone' in buildings_gdf.columns:
        print(f"\nBuildings by zone:")
        zone_counts = buildings_gdf['zone'].value_counts()
        for zone, count in zone_counts.items():
            pct = (count / total) * 100
            print(f"  {zone:15s}: {count:5d} buildings ({pct:5.1f}%)")
    
    if 'building_type' in buildings_gdf.columns:
        print(f"\nBuildings by type:")
        type_counts = buildings_gdf['building_type'].value_counts()
        for btype, count in type_counts.items():
            pct = (count / total) * 100
            print(f"  {btype:15s}: {count:5d} buildings ({pct:5.1f}%)")
    
    if 'household_type' in buildings_gdf.columns:
        print(f"\nBuildings by household type:")
        hh_counts = buildings_gdf['household_type'].value_counts()
        for hhtype, count in hh_counts.items():
            pct = (count / total) * 100
            print(f"  {hhtype:15s}: {count:5d} buildings ({pct:5.1f}%)")
    
    if 'unit_size' in buildings_gdf.columns:
        unit_sizes = buildings_gdf[buildings_gdf['unit_size'] > 0]['unit_size']
        if len(unit_sizes) > 0:
            print(f"\nUnit size statistics:")
            print(f"  Average unit size: {unit_sizes.mean():.1f} m²")
            print(f"  Min unit size: {unit_sizes.min():.1f} m²")
            print(f"  Max unit size: {unit_sizes.max():.1f} m²")
    
    if 'household_count' in buildings_gdf.columns:
        total_households = buildings_gdf['household_count'].sum()
        print(f"\nTotal households: {total_households}")
    
    if 'resident_count' in buildings_gdf.columns:
        total_residents = buildings_gdf['resident_count'].sum()
        print(f"Total residents: {total_residents}")
        
        # show household size distribution
        residential_buildings = buildings_gdf[buildings_gdf['building_type'] != 'none']
        if len(residential_buildings) > 0:
            print(f"\nHousehold size distribution:")
            household_sizes = []
            for _, row in residential_buildings.iterrows():
                if row['household_count'] > 0:
                    household_size = row['resident_count'] / row['household_count']
                    household_sizes.append(household_size)
            
            if household_sizes:
                print(f"  Average household size: {sum(household_sizes)/len(household_sizes):.1f} residents")
                print(f"  Min household size: {min(household_sizes):.0f} residents")
                print(f"  Max household size: {max(household_sizes):.0f} residents")
    
    print(f"{'='*60}")
