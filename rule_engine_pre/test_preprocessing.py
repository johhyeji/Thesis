from rule_dataclass import load_rules_from_yaml
from preprocessing import TemplateModifier


def main():
    # 1. load rules
    print("\n[1] Loading rules from YAML...")
    rules = load_rules_from_yaml("rule.yaml") # preprocessing.py // modify_template()
    print(rules)
    
    # 2. create modifier
    print("\n[2] Creating template modifier...")
    modifier = TemplateModifier(rules, random_seed=42)
    
    # 3. run preprocessing on Groningen npz
    print("\n[3] Preprocessing...")
    input_path = "../citystack/citypy/Groningen/Groningen_NL.npz"
    output_path = "Groningen_NL_modified.npz"
    
    stats = modifier.modify_template(
        input_path=input_path,
        output_path=output_path,
        cell_size=100.0  
    )
    
    # 4. print summary
    print("\n" + "="*70)
    print("PREPROCESSING COMPLETE")
    print("="*70)
    print(f"\nInput:  {input_path}")
    print(f"Output: {output_path}")
    print(f"\nTotal cells processed: {stats['total_cells']}")
    print(f"Zones covered: {list(stats['by_zone'].keys())}")
    print(f"Building types assigned: {list(stats['by_type'].keys())}")
    
    # show pct by type
    total = stats['total_cells']
    # print("‼️‼️")
    # print (stats)
    print("\n" + "-"*70)
    print("FINAL DISTRIBUTION:")
    print("-"*70)
    
    # residential vs non-residential
    residential_types = ['apartment', 'detached', 'terraced']
    residential_count = sum(stats['by_type'].get(t, 0) for t in residential_types)
    non_residential_count = stats['by_type'].get('none', 0)
    
    # num of landuse cells and percentages
    print(f"\n  LANDUSE SUMMARY:") # left aligned
    print(f"  {'Residential':<20}: {residential_count:6d} cells ({residential_count/total*100:5.1f}%)")
    print(f"  {'Non-residential':<20}: {non_residential_count:6d} cells ({non_residential_count/total*100:5.1f}%)")
    
    # num of residential cells by type and pct of total and pct of residential
    print(f"\n  RESIDENTIAL TYPE DISTRIBUTION:")
    for btype in residential_types:
        count = stats['by_type'].get(btype, 0)
        if count > 0:
            pct = (count / total) * 100
            res_pct = (count / residential_count * 100) if residential_count > 0 else 0
            print(f"  {btype:15s}: {count:6d} cells ({pct:5.1f}% of total, {res_pct:5.1f}% of residential)")
    
    print(f"\n  DETAILED BREAKDOWN BY ZONE:")
    print(f"  {'-'*66}")
    
    # sort zone by types
    for zone_name in sorted(stats['by_zone'].keys()):
        zone_total = stats['by_zone'][zone_name]
        zone_types = stats['by_zone_and_type'].get(zone_name, {})
        
        # get lanuse rule by zones (from RuleSet in rule_dataclass.py)
        landuse_rule = rules.get_landuse_rule(zone_name)
        housing_rule = rules.get_housing_rule(zone_name)
        expected_res_pct = landuse_rule.residential_pct * 100 if landuse_rule else 0
        
        # calculate actual residential count (from RulseSet)
        zone_residential = sum(zone_types.get(t, 0) for t in residential_types)
        zone_nonresidential = zone_types.get('none', 0)
        actual_res_pct = (zone_residential / zone_total * 100) if zone_total > 0 else 0
        
        print(f"\n  Zone: {zone_name} ({zone_total} cells)")
        print(f"    Landuse (residential): {zone_residential:4d} cells ({actual_res_pct:5.1f}%) [expected {expected_res_pct:.0f}%]")
        print(f"    Landuse (non-residential): {zone_nonresidential:4d} cells ({zone_nonresidential/zone_total*100:5.1f}%)")
        
        # show residential type distribution for this zone
        if zone_residential > 0:
            print(f"    Residential type distribution:")
            for btype in residential_types:
                count = zone_types.get(btype, 0)
                if count > 0:
                    pct_of_zone = (count / zone_total * 100)
                    pct_of_res = (count / zone_residential * 100)
                    
                    # get expected percentage from housing rule
                    if housing_rule:
                        if btype == 'apartment':
                            expected_pct = housing_rule.apartment_pct * 100
                        elif btype == 'detached':
                            expected_pct = housing_rule.detached_pct * 100
                        elif btype == 'terraced':
                            expected_pct = housing_rule.terraced_pct * 100
                        else:
                            expected_pct = 0
                        print(f"      {btype:10s}: {count:4d} ({pct_of_res:5.1f}% of residential, expected {expected_pct:.0f}%)")
                    else:
                        print(f"      {btype:10s}: {count:4d} ({pct_of_res:5.1f}% of residential)")
    
    print("\n" + "="*70)
    print("Modified template saved successfully.")
    print("="*70)



if __name__ == "__main__":
    main()

