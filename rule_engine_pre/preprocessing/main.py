import numpy as np
import sys
from pathlib import Path
from typing import Dict

# add parent directory to path for imports
PARENT_DIR = Path(__file__).parent.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from preprocessing.template_modifier import TemplateModifier
from rules.parser import RuleParser

# move all printing from template_modifier to here

def modify_template_with_stats(
    input_path: str,
    output_path: str,
    rules_yaml: str,
    cell_size: float = 100.0,
    random_seed: int = 42
) -> Dict:
    """
    Modify template with full statistics and printing
    
    Args:
        input_path: Path to input NPZ template
        output_path: Path to output NPZ template
        rules_yaml: Path to rules YAML file
        cell_size: Size of grid cells in meters
        random_seed: Random seed for reproducibility
        
    Returns:
        Dictionary with modification statistics
    """
    print(f"\n{'='*60}")
    print("PREPROCESSING: modify NPZ template")
    print('='*60)
    
    # 1. load rules
    print(f"\n[1] Loading rules from: {rules_yaml}")
    parser = RuleParser()
    rules = parser.load_from_yaml(rules_yaml)
    print(f"  Loaded {len(rules.zones)} zones")
    print(f"  Loaded {len(rules.housing_rules)} housing rules")
    print(f"  Loaded {len(rules.landuse_rules)} landuse rules")
    
    # 2. create modifier
    print(f"\n[2] Creating template modifier...")
    modifier = TemplateModifier(rules, random_seed=random_seed)
    print(f"  Initialized with random seed: {random_seed}")
    
    # 3. modify template
    print(f"\n[3] Modifying template...")
    print(f"  Input: {input_path}")
    print(f"  Output: {output_path}")
    
    stats = modifier.modify_template(input_path, output_path, cell_size)
    
    # 4. print statistics
    print(f"\n[4] Modification complete!")
    _print_preprocessing_statistics(stats)
    
    return stats


def _print_preprocessing_statistics(stats: Dict):
    """Print preprocessing statistics"""
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
