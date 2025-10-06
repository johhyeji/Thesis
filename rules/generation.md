# Rule-to-Layer Mapping 
Coupling rules to layer that should be generated.  
Layers used from CityStackGen: `city_center`, `streets`, `enclousres`, `buildings`

## Generation Layer Order
Each generation step builds upon the previous layers.

1. **Base Layer** — `City Zones` (e.g. 0–1km, 1–2km, 2–5km from center)
2. **Streets** 
3. **Enclosures** — closed blocks formed by streets 
4. **Building Blocks** — coarse building footprints, one per enclosure
5. **Buildings** — individual housing buildings split from blocks
6. **Households** — unit allocation per building (not spatial geometry, but attribute lo

## 1. Base Layer: City Zones (0–1km, 1–2km, etc.)
⚠️ conecntric patterns might be overgeneralizing city patterns.  

Divide the city into concentric rings around the city center, used to apply different rules by zone.

### Affected Rule(s):
- `Zones` — Zone distances (e.g., 1000, 2000, 5000 meters)
- (Used as context by all downstream rules)

### Output:
- Zonal `Polygon` layer (`zone = 0_1km`, `1_2km`, etc.)

---

## 2. Streets Layer

Street layer from CityStackGen.

### Affected Rule(s):


### Output:
- Line geometries with road class attributes
- Used to generate enclosures (closed street blocks)

---

## 3. Enclosure Layer
Identify enclosed spaces (closed loops) formed by the street network — becomes basis for block placement.

### Affected Rule(s):
- Indirectly inherits from street morphology

### Output:
- Polygon enclosures (street blocks)
- Attributes: `zone`, `enclosure_id`

---

## 4. Building Block Layer

Place a single coarse building footprint within each enclosure — "building mass" per block.

### Affected Rule(s):
- `lanuse percentage`


### Output:
- Polygon building blocks
- Attributes: `housing_type`, `height`, `floor_area`, `mixed_use`, `vacancy_rate`

---

## 5. Buildings Layer

Split each building block into multiple buildings — e.g., subdivide a block into row houses or apartment segments.

### Affected Rule(s):
- `Housing Type Mix` 

### Output:
- Polygon layer of individual buildings
- Attributes: `building_id`, `parent_block_id`, `type`, `num_unit`, `height`, etc.

---

## 6. Household Assignment Layer

Assign number of units and residents to each building using rules on density, unit size, and vacancy.

### Affected Rule(s):
- `Average Unit Size`
- `Average Household Size`
- `Number of Residents`


### Output:
- Attributes per building:
  - `avg_unit_size`, `household_type`, `residents`

---

