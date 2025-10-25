# Rule-Driven City Generation System

This document describes the rule system for controlling synthetic city generation. Rules are defined in YAML configuration files and control building types, street patterns, household distribution, and urban form.

---

## Overview

Rules are applied through a **three-stage pipeline**:

### Pipeline Stages

```
┌──────────────────────────────────────────────────────────────┐
│ 1. PREPROCESSING (Python - Rule Engine)                      │
│    - Modify building class grid in template                  │
│    - Modify street cluster templates                         │
│    Input: Original template + clusters + rules               │
│    Output: Modified template + modified clusters             │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. GENERATION (Rust - CityStackGen)                          │
│    - Generate street network geometry                        │
│    - Generate building footprints                            │
│    - Generate enclosures                                     │
│    Input: Modified template + modified clusters              │
│    Output: GeoJSON layers (streets, buildings, enclosures)   │
│    NOTE: CityStackGen code is UNCHANGED                      │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. POSTPROCESSING (Python - Rule Engine)                     │
│    - Classify/reclassify buildings                           │
│    - Modify street geometry                                  │
│    - Assign households                                       │
│    - Apply constraints and validation                        │
│    Input: Generated GeoJSON + rules                          │
│    Output: Final layers + households.csv + statistics        │
└──────────────────────────────────────────────────────────────┘
```

---

## Rule Categories

Rules are organized by **when they are applied** in the pipeline:

### Quick Reference Table

| Rule Type | Stage | Purpose | YAML Key |
|-----------|-------|---------|----------|
| **Zone Definitions** | Setup | Define distance zones from city center | `zones` |
| **Housing Type Mix** | Preprocessing | Modify building class grid | `housing_type_rules` |
| **Street Templates** | Preprocessing | Modify cluster JSON distributions | `street_template_rules` |
| **Housing Type Mix** | Postprocessing | Assign building classes to geometry | `housing_type_rules` |
| **Spatial Rules** | Postprocessing | Condition-based building classification | `spatial` |
| **Morphological Rules** | Postprocessing | Building method based on enclosures | `morphological` |
| **Street Geometry** | Postprocessing | Modify street LineStrings | `street_geometry_rules` |
| **Demographic Rules** | Postprocessing | Household density by building class | `demographic` |
| **Residents** | Postprocessing | Population density per zone | `residents_rules` |
| **Unit Size** | Postprocessing | Floor area ranges per zone | `unit_size_rules` |
| **Household Types** | Postprocessing | Household composition per zone | `household_type_rules` |
| **Landuse** | Postprocessing | Residential percentage per zone | `landuse_rules` |
| **Constraints** | Postprocessing | Validation rules | `constraint_rules` |

---

# PART 1: PREPROCESSING RULES

These rules modify inputs **before** CityStackGen runs.

---

### 1. Zone Definitions

Defines concentric zones from the city center. Used across both preprocessing and postprocessing.

**YAML Format:**
```yaml
zones:
  - name: "0_1km"
    min_distance: 0      # meters from city center
    max_distance: 1000
  - name: "1_2km"
    min_distance: 1000
    max_distance: 2000
  - name: "2_5km"
    min_distance: 2000
    max_distance: 5000
```

**When Applied:** Setup (referenced throughout pipeline)

**Purpose:**
- City center coordinates come from CityPy dataset
- Used for per-zone demographic and housing rules
- Applied in both preprocessing (template modification) and postprocessing (household assignment)

---

### 2. Housing Type Mix (Preprocessing)

Distribution of housing types per zone, applied to the building class grid in the template.

**YAML Format:**
```yaml
housing_type_rules:
  - zone: "0_1km"
    apartment_pct: 0.80   # 80%
    terraced_pct: 0.15    # 15%
    detached_pct: 0.05    # 5%
  - zone: "1_2km"
    apartment_pct: 0.50
    terraced_pct: 0.30
    detached_pct: 0.20
  - zone: "2_5km"
    apartment_pct: 0.20
    terraced_pct: 0.40
    detached_pct: 0.40
```

**When Applied:** Preprocessing - modifies `building_class` grid in template NPZ file

**Purpose:**
- Pre-assigns building types to grid cells based on distance from city center
- CityStackGen uses this modified grid to guide building generation
- Can be further refined in postprocessing

**Building Class Mapping:**
- `apartments`: 14
- `terraced`: 22
- `detached`: 17

---

### 3. Street Template Rules

Modify street cluster templates before generation by adjusting statistical distributions.

**YAML Format:**
```yaml
street_template_rules:
  - cluster_id: 0
    rule_type: "segment_length"
    action: "scale_lengths=1.2"
    weight: 0.8
  - cluster_id: 1
    rule_type: "intersection_degree"
    action: "increase_degrees=0.5"
    weight: 0.7
  - cluster_id: 2
    rule_type: "forward_angle"
    action: "adjust_angles=0.9"
    weight: 0.6
```

**When Applied:** Preprocessing - modifies cluster JSON files before CityStackGen runs

**Rule Types:**
- `segment_length`: Scale street segment lengths (e.g., make streets 20% longer)
- `intersection_degree`: Modify intersection complexity (more/fewer connections)
- `forward_angle`: Adjust street curvature (straighter vs. curvier)

**Actions:**
- `scale_lengths=<factor>`: Multiply length distribution by factor (e.g., 1.2 = 20% longer)
- `increase_degrees=<amount>`: Shift degree distribution by amount
- `adjust_angles=<factor>`: Modify angle distribution

**Purpose:**
- Control street network characteristics before generation
- Useful for creating denser/sparser networks
- Affects how CityStackGen generates street geometry

---

# PART 2: POSTPROCESSING RULES

These rules are applied **after** CityStackGen generates geometry.

---

### 4. Housing Type Mix (Postprocessing)

Same rules as preprocessing, but applied to generated building footprints for fine-tuning.

**When Applied:** Postprocessing - assigns `building_class` to generated building polygons

**Purpose:**
- Reclassify buildings based on actual geometry
- Override preprocessing assignments if needed
- More accurate than grid-based preprocessing

---

### 5. Spatial Rules

Control building classification based on distance or other spatial properties.

**YAML Format:**
```yaml
spatial:
  - condition: "distance_to_center < 300"
    action: "building_class = 'apartments'"
    weight: 0.9
  - condition: "distance_to_center >= 300 and distance_to_center < 800"
    action: "building_class = 'detached'"
    weight: 0.8
```

**When Applied:** Postprocessing - assigns building classes to generated buildings

**Purpose:**
- Alternative to zone-based rules
- More flexible condition-based logic
- Can use complex boolean expressions

**Variables Available:**
- `distance_to_center`: Distance from building centroid to city center (meters)
- Conditions use Python-style expressions
- `weight` controls probability (0.0-1.0)

---

### 6. Morphological Rules

Control building classification based on enclosure properties.

**YAML Format:**
```yaml
morphological:
  - condition: "enclosure_area > 5000"
    action: "method = 'oobb'"
    weight: 0.7
  - condition: "enclosure_area <= 5000"
    action: "method = 'sweep'"
    weight: 0.6
```

**When Applied:** Postprocessing - affects how buildings are classified/processed

**Variables Available:**
- `enclosure_area`: Area of the enclosure containing the building (m²)

**Methods:**
- `oobb`: Oriented bounding box (better for larger plots)
- `sweep`: Straight skeleton sweep (better for complex shapes)

---

### 7. Street Geometry Rules

Modify generated street geometry.

**YAML Format:**
```yaml
street_geometry_rules:
  - condition: "distance_to_center < 500"
    action: "simplify=1.0"
    rule_type: "geometry"
    weight: 0.8
  - condition: "street_length > 200"
    action: "split=100"
    rule_type: "geometry"
    weight: 0.7
```

**When Applied:** Postprocessing - modifies generated street LineStrings

**Actions:**
- `simplify=<tolerance>`: Simplify geometry (remove redundant vertices)
- `split=<length>`: Split long streets into segments
- `extend=<distance>`: Extend street segments
- `smooth=<tolerance>`: Apply smoothing

**Variables Available:**
- `distance_to_center`: Distance from street to city center (meters)
- `street_length`: Length of street segment (meters)

---

### 8. Demographic Rules

Control household density based on building class.

**YAML Format:**
```yaml
demographic:
  - condition: "building_class = 14"  # apartments
    action: "household_density = 2.5"
    weight: 0.9
  - condition: "building_class = 17"  # detached
    action: "household_density = 1.0"
    weight: 0.8
  - condition: "building_class = 22"  # terraced
    action: "household_density = 1.5"
    weight: 0.8
```

**When Applied:** Postprocessing - used during household assignment

**Purpose:**
- Controls how many households are assigned per building
- Higher density for apartments (multiple units)
- Lower density for detached homes (single family)

---

### 9. Number of Residents

Average number of residents per 100m x 100m grid per zone.

**YAML Format:**
```yaml
residents_rules:
  - zone: "0_1km"
    residents_per_grid: 800
  - zone: "1_2km"
    residents_per_grid: 600
  - zone: "2_5km"
    residents_per_grid: 350
```

**When Applied:** Postprocessing - used during household assignment

**Purpose:**
- Controls target population density per zone
- Higher values = denser urban core
- Lower values = suburban/rural areas
- Used to calculate number of households needed in each building

---

### 10. Unit Size

Typical floor area (m²) per housing unit, based on zone.

**YAML Format:**
```yaml
unit_size_rules:
  - zone: "0_1km"
    min_size: 40   # m²
    max_size: 60
  - zone: "1_2km"
    min_size: 60
    max_size: 80
  - zone: "2_5km"
    min_size: 90
    max_size: 120
```

**When Applied:** Postprocessing - used during household assignment and validation

**Purpose:**
- Smaller units in urban cores (studio apartments)
- Larger units in suburbs (family homes)
- Used for household assignment validation with constraints
- Helps determine realistic household counts per building

---

### 11. Household Types

Distribution of household types per zone.

**YAML Format:**
```yaml
household_type_rules:
  - zone: "0_1km"
    single_person_pct: 0.50          # 50%
    two_parent_pct: 0.20             # 20%
    single_parent_pct: 0.10          # 10%
    without_children_pct: 0.20       # 20%
  - zone: "1_2km"
    single_person_pct: 0.35
    two_parent_pct: 0.30
    single_parent_pct: 0.15
    without_children_pct: 0.20
  - zone: "2_5km"
    single_person_pct: 0.20
    two_parent_pct: 0.45
    single_parent_pct: 0.15
    without_children_pct: 0.20
```

**When Applied:** Postprocessing - used during household assignment

**Household Types:**
- `single_person`: 1-person households
- `two_parent`: Families with two parents and children
- `single_parent`: Single-parent families with children
- `without_children`: Couples or multi-person households without children

**Purpose:**
- Creates realistic demographic distributions
- Urban cores have more single-person households
- Suburbs have more family households

---

### 12. Landuse Percentage

Percentage of residential landuse in a given zone.

**YAML Format:**
```yaml
landuse_rules:
  - zone: "0_1km"
    residential_pct: 0.20  # 20% residential
  - zone: "1_2km"
    residential_pct: 0.60  # 60% residential
  - zone: "2_5km"
    residential_pct: 0.80  # 80% residential
```

**When Applied:** Postprocessing - used for filtering/classifying buildings

**Purpose:**
- Rest is 'other' (commercial, industrial, mixed-use, etc.)
- Urban cores often have lower residential % due to commercial use
- Used to filter which buildings get residential households

---

### 13. Constraints

Ensures plausible combinations (prevents unrealistic outputs).

**YAML Format:**
```yaml
constraint_rules:
  - rule_type: "unit_size_vs_housing_type"
    condition: "unit_size < 30"
    constraint: "must be apartment"
    description: "Units smaller than 30m² must be apartments"
  - rule_type: "household_size_vs_unit_size"
    condition: "average_household_size > 3"
    constraint: "unit_size must be > 80"
    description: "Large households need units larger than 80m²"
```

**When Applied:** Postprocessing - validation during household assignment

**Common Constraints:**
- Small units (< 30m²) → must be apartments
- Large households (> 3 people) → need larger units (> 80m²)
- Detached houses → typically > 90m²

**Purpose:**
- Prevents physically impossible combinations
- Ensures demographic realism
- Validates household assignments before finalizing

---

---

# PART 3: COMPLETE CONFIGURATION EXAMPLES

---

## Example 1: Dense Urban Configuration

**File:** `rule_engine/examples/groningen_dense_urban.yaml`

**Characteristics:**
- High-rise apartments in urban core (0-1km)
- Small unit sizes (40-60m²)
- High single-person household percentage (50%)
- Tight street grid with simplified geometry

**Rules Applied:**

*Preprocessing:*
- Zone-based housing type mix (80% apartments in core)
- Street template modifications (scale_lengths=0.9 for tighter grid)

*Postprocessing:*
- Demographic rules (household_density=2.5 for apartments)
- Residents rules (800 per grid in 0-1km zone)
- Unit size validation (40-60m² in core)
- Household type distribution (50% single-person in core)

---

## Example 2: Suburban Configuration

**File:** `rule_engine/examples/suburban_rules.yaml`

**Characteristics:**
- Detached houses dominate (>80%)
- Larger unit sizes (90-120m²)
- Family households predominant (45% two-parent)
- Wider, extended streets

**Rules Applied:**

*Preprocessing:*
- Spatial rules (detached houses beyond 300m from center)

*Postprocessing:*
- Demographic rules (household_density=1.0 for detached)
- Street geometry rules (extend=25.0 for longer streets)
- Street template modifications (scale_lengths=1.3 for wider spacing)

---

## Example 3: Mixed-Use Configuration

**File:** `rule_engine/examples/mixed_use_rules.yaml`

**Characteristics:**
- Balanced housing types across zones
- Terraced houses in middle ring (1-2km: 40%)
- Gradient from urban to suburban
- Varied street patterns by distance

**Rules Applied:**

*Both preprocessing and postprocessing:*
- Zone-based gradual transitions
- Moderate densities throughout
- Balanced household types

---

# PART 4: USAGE & REFERENCE

---

## Usage

### 1. Create a YAML Configuration File

Choose rule types based on what stage you want to control:

```yaml
# Preprocessing rules (modify inputs before generation)
zones: [...]
housing_type_rules: [...]
street_template_rules: [...]

# Postprocessing rules (modify outputs after generation)
residents_rules: [...]
unit_size_rules: [...]
household_type_rules: [...]
landuse_rules: [...]
constraint_rules: [...]
street_geometry_rules: [...]
demographic: [...]
spatial: [...]
morphological: [...]
```

### 2. Run the Generator

```python
from rule_engine import RuleDrivenCityGenerator

generator = RuleDrivenCityGenerator(
    rules_path="path/to/rules.yaml",
    citystackgen_path="citystack/citystackgen"
)

result = generator.generate_city(
    original_template_path="template.npz",
    cluster_dir="clusters/",
    city_center=(x, y),
    output_dir="outputs/"
)
```

### 3. Review Outputs

**Preprocessing outputs:**
- `template_modified.npz`: Modified building class grid
- `clusters_modified/`: Modified street cluster templates

**Generation outputs** (from CityStackGen):
- Raw GeoJSON layers (overwritten by postprocessing)

**Postprocessing outputs:**
- `streets_modified.geojson`: Final street network
- `buildings_with_classes.geojson`: Buildings with assigned classes
- `households.csv`: Household assignments with demographics
- `statistics.json`: Comprehensive validation statistics

---

## Building Class Reference

Complete mapping of building class names to IDs:

| Class ID | Name | Description |
|----------|------|-------------|
| 14 | `apartments` | Multi-unit residential buildings |
| 15 | `big_commercial` | Large commercial structures |
| 16 | `complex` | Complex building arrangements |
| 17 | `detached` | Single-family detached houses |
| 18 | `filled_block` | Dense urban block fills |
| 19 | `industrial` | Industrial/warehouse buildings |
| 20 | `irregular_block` | Irregular block patterns |
| 21 | `perimeter_block` | Buildings around block perimeter |
| 22 | `terraced` | Row houses/terraced housing |
| 99 | `none` | Unclassified/other |

**Primary Residential Types:**
- Apartments (14): High-density, multiple units per building
- Terraced (22): Medium-density, attached row houses
- Detached (17): Low-density, single-family homes

---

## Implementation Architecture

```
rule_engine/
├── rules/
│   ├── types.py              # Rule dataclass definitions
│   ├── parser.py             # YAML → RuleSet conversion
│   └── executor.py           # Rule evaluation logic
├── preprocessing/
│   ├── template_modifier.py         # Modify NPZ templates
│   └── street_template_modifier.py  # Modify cluster JSONs
├── interfaces/
│   └── citystackgen_interface.py    # CLI wrapper for CityStackGen
├── postprocessing/
│   ├── building_processor.py        # Apply building rules
│   ├── street_processor.py          # Apply street rules
│   └── household_assigner.py        # Assign households
└── main.py                           # Orchestration pipeline
```

---

## Tips & Best Practices

1. **Start with preprocessing rules** for coarse control (housing mix, street templates)
2. **Add postprocessing rules** for fine-grained adjustments (households, constraints)
3. **Use zone-based rules** for demographic/household parameters
4. **Use spatial/morphological rules** for flexible building classification
5. **Always include constraints** to prevent unrealistic outputs
6. **Test incrementally**: Add rules gradually and check statistics.json
7. **Visualize in QGIS**: Open GeoJSON outputs to see spatial patterns
8. **Compare variations**: Generate multiple cities with different rules to test sensitivity


