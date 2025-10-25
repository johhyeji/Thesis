from dataclasses import dataclass, field
from typing import List, Optional


### ZONE RULES

@dataclass
class Zone:
    # distance range from the city center. min and max in meters
    name: str
    min_distance: float
    max_distance: float

    def contains(self, distance: float) -> bool:
        # check if a distance falls within the stated zone.
        return self.min_distance <= distance < self.max_distance
    
    def __str__(self):
        return f"Zone('{self.name}': {self.min_distance}-{self.max_distance}m)"


@ dataclass
class HousingRule:
    # housing mix rule for each zone, in percentages
    zone: str
    apartment_pct: float
    detached_pct: float
    terraced_pct: float

    # check that the percentages sum to 1.0
    def __post_init__(self):
        total = self.apartment_pct + self.detached_pct + self.terraced_pct

        # check for floating point errors
        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Housing percentages must sum to 1.0, got {total:.3f}\n"
                f"  apartment: {self.apartment_pct}\n"
                f"  detached: {self.detached_pct}\n"
                f"  terraced: {self.terraced_pct}"
            )
    
    def __str__(self):
        return (f"HousingRule(zone = '{self.zone}': "
                f"{self.apartment_pct:.0%} apt, "
                f"{self.detached_pct:.0%} detached, "
                f"{self.terraced_pct:.0%} terraced)")

### PREPROCESSING ONLY
# landuse rule
@ dataclass
class LanduseRule:
    zone: str
    residential_pct: float

    def __post_init__(self):
        if not (0.0 <= self.residential_pct <= 1.0):
            raise ValueError(f"Residential percentage must be between 0.0 and 1.0, got {self.residential_pct}")
    
    def __str__(self):
        return f"LanduseRule(zone = '{self.zone}': {self.residential_pct:.0%})"

### POSTPROCESSING ONLY
@ dataclass
# add a household rule
class HouseholdRule:
    zone: str
    single_person_pct: float
    single_parent_pct: float
    two_parent_pct: float

    def __post_init__(self):
        total = self.single_person_pct + self.single_parent_pct + self.two_parent_pct

        if not (0.99 <= total <= 1.01):
            raise ValueError(
                f"Household percentages must sum to 1.0, got {total:.3f}\n"
                f"  single_person: {self.single_person_pct}\n"
                f"  single_parent: {self.single_parent_pct}\n"
                f"  two_parent: {self.two_parent_pct}"
            )
    
    def __str__(self):
        return (f"HouseholdRule(zone = '{self.zone}': "
                f"{self.single_person_pct:.0%} single_person, "
                f"{self.single_parent_pct:.0%} single_parent, "
                f"{self.two_parent_pct:.0%} two_parent)")
    

# RuleSet: container for all rules
@ dataclass
class RuleSet:
    zones: List[Zone]
    housing_rules: List[HousingRule]
    landuse_rules: List[LanduseRule]
    household_rules: List[HouseholdRule]

    # find which zone a distance belongs to
    # e.g. ruleset.get_zone(500) -> Zone('0_1km': 0-1000m)
    def get_zone(self, distance: float) -> Zone:
        for zone in self.zones:
            if zone.contains(distance):
                return zone
        return None

    # get housing rule for a specific zone
    # e.g. ruleset.get_housing_rule('0_1km') -> HousingRule(zone = '0_1km': 80% apt, 20% detached)
    def get_housing_rule(self, zone_name: str) -> HousingRule:
        for rule in self.housing_rules:
            if rule.zone == zone_name:
                return rule
        return None
    
    # get landuse rule for a specific zone
    def get_landuse_rule(self, zone_name: str) -> LanduseRule:
        for rule in self.landuse_rules:
            if rule.zone == zone_name:
                return rule
        return None
    
    # get household rule for a specific zone
    def get_household_rule(self, zone_name: str) -> HouseholdRule:
        for rule in self.household_rules:
            if rule.zone == zone_name:
                return rule
        return None
    
    def __str__(self):
        s = "RuleSet:\n"
        s += f"  Zones: {len(self.zones)}\n"
        for zone in self.zones:
            s += f"    - {zone}\n"
        s += f"  Housing Rules: {len(self.housing_rules)}\n"
        for rule in self.housing_rules:
            s += f"    - {rule}\n"
        s += f"  Landuse Rules: {len(self.landuse_rules)}\n"
        for rule in self.landuse_rules:
            s += f"    - {rule}\n"
        s += f"  Household Rules: {len(self.household_rules)}\n"
        for rule in self.household_rules:
            s += f"    - {rule}\n"
        return s





