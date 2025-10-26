import sys
import random
from pathlib import Path
from preprocessing.main import modify_template_with_stats
from postprocessing.main import postprocess_citystackgen_output


def main():
    # paths
    rules_yaml = "rule.yaml"
    input_template = "../citystack/citypy/outputs/Groningen/Groningen_NL.npz"
    preprocessing_output = "outputs/pre/Groningen_NL_modified.npz"
    
    buildings_geojson = "../citystack/citystackgen/outputs/Groningen_modified_2.1/buildings.geojson"
    city_center_geojson = "../citystack/citystackgen/outputs/Groningen_modified_2.1/city_center.geojson"
    postprocessing_output_geojson = "outputs/post/buildings_classified.geojson"
    postprocessing_output_csv = "outputs/post/buildings_classified.csv"
    
    random_seed = None  
    
    # if random_seed is None, generate one seed for both preprocessing and postprocessing
    if random_seed is None:
        random_seed = random.randint(0, 1000000)
        print(f"Random seed not provided, generated: {random_seed}") 
    if random_seed is not None:
        print(f"Random seed is provided: {random_seed}") 
    
    # preprocessing
    print("\n1. PREPROCESSING")
    print("-" * 40)
    modify_template_with_stats(
        input_path=input_template,
        output_path=preprocessing_output,
        rules_yaml=rules_yaml,
        cell_size=100.0,
        random_seed=random_seed
    )
    
    # postprocessing
    print("\n2. POSTPROCESSING")
    print("-" * 40)
    postprocess_citystackgen_output(
        buildings_geojson=buildings_geojson,
        city_center_geojson=city_center_geojson,
        rules_yaml=rules_yaml,
        output_geojson=postprocessing_output_geojson,
        output_csv=postprocessing_output_csv,
        random_seed=random_seed
    )
    
    # directory
    print(f"\nOutputs:")
    print(f"  Preprocessing:  {preprocessing_output}")
    print(f"  Postprocessing GeoJSON: {postprocessing_output_geojson}")
    print(f"  Postprocessing CSV: {postprocessing_output_csv}")


if __name__ == "__main__":
    main()

