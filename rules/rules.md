# Rule Categories

This is a preliminary working list of rules to define how the synthetic city is generated. These rules are:
- User-defined via CLI and `.yaml` config
- Zone-aware (e.g. per 0–1km, 1–2km buffer from city center)

---

## 1. Zones
Defines concentric zones from the city center to allow different rule values for each zone.
- Example zones:
  - `0_1km`
  - `1_2km`
  - `2_5km`
  - `5_7km`
- 'city_center' comes from CityPy dataset

---

## 2. Number of Residents
Average number of residents per 100m x 100m grid per zone. (will grids still be used with the concentric zoning?)
- Example:
  - `0_1km: 800`
  - `1_2km: 600`
  - `2_5km: 350`

---

## 3. Landuse Percentage (%)
Percentage of 'landuse == residential' in a given zone
- Example:
  - `0_1km: 20%`
  - `1_2km: 60%`
  - `2_5km: 80%`

The rest is 'others'.

---

## 4. Housing Type Mix (%)
Distribution of housing types per zone:
- `apartment`, `terraced`, `detached`
- Example:
  - `0_1km: apartment 80%, terraced 15%, detached 5%`
  - `1_2km: apartment 50%, terraced 30%, detached 20%`
  - `2_5km: apartment 20%, terraced 40%, detached 40%`

---

## 5. Range of Unit Size (m²)
Typical floor area per housing unit, based on zone, providing min and max.
- Example:
  - unit_size_by_zone:
    - 0_1km:
      - min: 40
      - max: 60
    - 1_2km:
      - min: 60
      - max: 80
    - 2_5km:
      - min: 90
      - max: 120

---

## 6. Type of Households
Single-person, two-parent, single-parent, household without children

## Constraints
To ensure plausible combinations. E.g. a detached house of 15 square meters is unrealistic
- unit size vs. housing type
  - if unit_size is < 30m2: must be `apartment`
- household size vs. unit size
  - if average_household_size < 3: must have unit size > 80m2
  


## Optional 
- arrangement of buildings using road types?
- housing type distribution by building height? (building height > 15m is an apartment, etc. )

