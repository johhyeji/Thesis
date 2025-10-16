from dataclasses import dataclass
from typing import List
import yaml


@ dataclass
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

# RuleSet: container for all rules
@ dataclass
class RuleSet:
    zones: List[Zone]
    housing_rules: List[HousingRule]

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
    
    def __str__(self):
        s = "RuleSet:\n"
        s += f"  Zones: {len(self.zones)}\n"
        for zone in self.zones:
            s += f"    - {zone}\n"
        s += f"  Housing Rules: {len(self.housing_rules)}\n"
        for rule in self.housing_rules:
            s += f"    - {rule}\n"
        return s


def load_rules_from_yaml(yaml_path: str) -> RuleSet:
    # load rules from the yaml file and convert to RuleSet object
    # reads and creates python objects

    # read yaml
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)

    # parse zones
    zones = []
    for zone_data in data.get('zones', []):
        zone = Zone(
            name = zone_data['name'],
            min_distance = float(zone_data['min_distance']),
            max_distance = float(zone_data['max_distance'])
        )
        zones.append(zone)

    # parse housing rules
    housing_rules = []
    for rule_data in data.get('housing_rules', []):
        rule = HousingRule(
            zone = rule_data['zone'],
            apartment_pct = float(rule_data['apartment_pct']),
            detached_pct = float(rule_data['detached_pct']),
            terraced_pct = float(rule_data['terraced_pct'])
        )
        housing_rules.append(rule)
    
    # parse landuse rules
    landuse_rules = []
    for rule_data in data.get('landuse_rules', []):
        rule = LanduseRule(
            zone = rule_data['zone'],
            residential_pct = float(rule_data['residential_pct'])
        )
        landuse_rules.append(rule)
    
    return RuleSet(zones=zones, housing_rules=housing_rules, landuse_rules=landuse_rules)





