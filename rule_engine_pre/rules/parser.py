import yaml
from pathlib import Path
from typing import Union

from .rule_dataclass import (
    RuleSet,
    Zone,
    HousingRule,
    LanduseRule,
    HouseholdRule,
    ResidentsRule,
    UnitSizeRule
)


# parse for YAML files into RuleSet objects
class RuleParser:
    # load rules from YAML file
    def load_from_yaml(self, filepath: Union[str, Path]) -> RuleSet:
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Rule file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            data = {}
        
        return RuleSet(
            zones=self._parse_zones(data.get('zones', [])),
            housing_rules=self._parse_housing_rules(data.get('housing_rules', [])),
            landuse_rules=self._parse_landuse_rules(data.get('landuse_rules', [])),
            household_rules=self._parse_household_rules(data.get('household_rules', [])),
            residents_rules=self._parse_residents_rules(data.get('residents_rules', [])),
            unit_size_rules=self._parse_unit_size_rules(data.get('unit_size_rules', []))
        )
    
    def _parse_zones(self, zones_data: list) -> list:
        # parse zone definitions
        return [
            Zone(
                name=zone.get('name', ''),
                min_distance=float(zone.get('min_distance', 0)),
                max_distance=float(zone.get('max_distance', 0))
            )
            for zone in zones_data
        ]
    
    def _parse_housing_rules(self, rules_data: list) -> list:
        # parse housing rules
        return [
            HousingRule(
                zone=rule.get('zone', ''),
                apartment_pct=float(rule.get('apartment_pct', 0.0)),
                detached_pct=float(rule.get('detached_pct', 0.0)),
                terraced_pct=float(rule.get('terraced_pct', 0.0))
            )
            for rule in rules_data
        ]
    
    def _parse_landuse_rules(self, rules_data: list) -> list:
        # parse landuse rules
        return [
            LanduseRule(
                zone=rule.get('zone', ''),
                residential_pct=float(rule.get('residential_pct', 0.0))
            )
            for rule in rules_data
        ]
    
    def _parse_household_rules(self, rules_data: list) -> list:
        # parse household rules
        return [
            HouseholdRule(
                zone=rule.get('zone', ''),
                single_person_pct=float(rule.get('single_person_pct', 0.0)),
                single_parent_pct=float(rule.get('single_parent_pct', 0.0)),
                two_parent_pct=float(rule.get('two_parent_pct', 0.0))
            )
            for rule in rules_data
        ]

    def _parse_residents_rules(self, rules_data: list) -> list:
        # parse residents rules
        return [
            ResidentsRule(
                zone=rule.get('zone', ''),
                residents_per_grid=float(rule.get('residents_per_grid', 0.0))
            )
            for rule in rules_data
        ]           
    
    def _parse_unit_size_rules(self, rules_data: list) -> list:
        # parse unit size rules
        return [
            UnitSizeRule(
                zone=rule.get('zone', ''),
                min_size=float(rule.get('min_size', 0.0)),
                max_size=float(rule.get('max_size', 0.0))
            )
            for rule in rules_data
        ]