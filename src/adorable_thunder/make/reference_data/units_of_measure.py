from typing import NamedTuple


class UnitOfMeasure(NamedTuple):
    code: str
    description: str
    category: str


# Codes follow UN/CEFACT Recommendation 20 and GS1 standards
UNITS_OF_MEASURE: list[UnitOfMeasure] = [
    # Count
    UnitOfMeasure("EA", "Each", "count"),
    UnitOfMeasure("BX", "Box", "count"),
    UnitOfMeasure("CS", "Case", "count"),
    UnitOfMeasure("PK", "Package", "count"),
    UnitOfMeasure("ST", "Set", "count"),
    UnitOfMeasure("PR", "Pair", "count"),
    UnitOfMeasure("DZ", "Dozen", "count"),
    UnitOfMeasure("PL", "Pallet", "count"),
    # Weight
    UnitOfMeasure("KG", "Kilogram", "weight"),
    UnitOfMeasure("LB", "Pound", "weight"),
    UnitOfMeasure("MT", "Metric Ton", "weight"),
    UnitOfMeasure("G", "Gram", "weight"),
    UnitOfMeasure("OZ", "Ounce", "weight"),
    # Volume
    UnitOfMeasure("LT", "Liter", "volume"),
    UnitOfMeasure("GL", "Gallon", "volume"),
    UnitOfMeasure("ML", "Milliliter", "volume"),
    UnitOfMeasure("CBM", "Cubic Meter", "volume"),
    # Length / Area
    UnitOfMeasure("M", "Meter", "length"),
    UnitOfMeasure("FT", "Foot", "length"),
    UnitOfMeasure("IN", "Inch", "length"),
    UnitOfMeasure("SQM", "Square Meter", "area"),
    UnitOfMeasure("SFT", "Square Foot", "area"),
    # Time
    UnitOfMeasure("HR", "Hour", "time"),
    UnitOfMeasure("DAY", "Day", "time"),
    UnitOfMeasure("MO", "Month", "time"),
    UnitOfMeasure("YR", "Year", "time"),
    # Service / Digital
    UnitOfMeasure("LIC", "License", "service"),
    UnitOfMeasure("SVC", "Service Unit", "service"),
    UnitOfMeasure("USR", "User Seat", "service"),
    UnitOfMeasure("API", "API Call", "digital"),
    UnitOfMeasure("GB", "Gigabyte", "digital"),
    UnitOfMeasure("TB", "Terabyte", "digital"),
]
