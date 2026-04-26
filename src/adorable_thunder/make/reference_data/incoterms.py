from typing import NamedTuple


class Incoterm(NamedTuple):
    code: str
    name: str
    applicable_transport: str


# Incoterms 2020 — all 11 rules published by the International Chamber of Commerce
INCOTERMS: list[Incoterm] = [
    # Rules for any mode of transport
    Incoterm("EXW", "Ex Works", "any"),
    Incoterm("FCA", "Free Carrier", "any"),
    Incoterm("CPT", "Carriage Paid To", "any"),
    Incoterm("CIP", "Carriage and Insurance Paid To", "any"),
    Incoterm("DAP", "Delivered at Place", "any"),
    Incoterm("DPU", "Delivered at Place Unloaded", "any"),
    Incoterm("DDP", "Delivered Duty Paid", "any"),
    # Rules for sea and inland waterway transport only
    Incoterm("FAS", "Free Alongside Ship", "sea"),
    Incoterm("FOB", "Free on Board", "sea"),
    Incoterm("CFR", "Cost and Freight", "sea"),
    Incoterm("CIF", "Cost Insurance and Freight", "sea"),
]
