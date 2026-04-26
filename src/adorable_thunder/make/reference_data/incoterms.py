# (code, name, applicable_transport)
# Incoterms 2020 — all 11 rules published by the International Chamber of Commerce
INCOTERMS = [
    # Rules for any mode of transport
    ("EXW", "Ex Works", "any"),
    ("FCA", "Free Carrier", "any"),
    ("CPT", "Carriage Paid To", "any"),
    ("CIP", "Carriage and Insurance Paid To", "any"),
    ("DAP", "Delivered at Place", "any"),
    ("DPU", "Delivered at Place Unloaded", "any"),
    ("DDP", "Delivered Duty Paid", "any"),
    # Rules for sea and inland waterway transport only
    ("FAS", "Free Alongside Ship", "sea"),
    ("FOB", "Free on Board", "sea"),
    ("CFR", "Cost and Freight", "sea"),
    ("CIF", "Cost Insurance and Freight", "sea"),
]
