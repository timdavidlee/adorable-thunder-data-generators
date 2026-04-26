# (scac_code, carrier_name, primary_mode)
# SCAC = Standard Carrier Alpha Code (4-letter industry identifier)
CARRIERS = [
    # Road — North America
    ("JBHT", "J.B. Hunt Transport Services", "road"),
    ("ODFL", "Old Dominion Freight Line", "road"),
    ("SAIA", "Saia Inc.", "road"),
    ("RLCA", "R+L Carriers", "road"),
    ("ABFS", "ABF Freight System", "road"),
    ("FXFE", "FedEx Freight", "road"),
    ("UPGF", "UPS Freight", "road"),
    ("EXLA", "Estes Express Lines", "road"),
    # Road — International / Europe
    ("DHLF", "DHL Freight", "road"),
    ("DSVS", "DSV Road", "road"),
    ("DBSC", "DB Schenker Road", "road"),
    ("KNET", "Kuehne+Nagel Road", "road"),
    # Parcel / Express
    ("FDXG", "FedEx Ground", "parcel"),
    ("UPSN", "UPS", "parcel"),
    ("USPS", "USPS", "parcel"),
    ("DHLE", "DHL Express", "parcel"),
    ("TNTE", "TNT Express", "parcel"),
    ("DPWG", "DPD", "parcel"),
    # Ocean
    ("MAEU", "Maersk", "ocean"),
    ("MSCU", "MSC", "ocean"),
    ("COSU", "COSCO Shipping", "ocean"),
    ("HLCU", "Hapag-Lloyd", "ocean"),
    ("EGLV", "Evergreen", "ocean"),
    ("CMDU", "CMA CGM", "ocean"),
    ("ONEY", "ONE (Ocean Network Express)", "ocean"),
    ("YMLU", "Yang Ming", "ocean"),
    # Air Freight
    ("FXAI", "FedEx Express", "air"),
    ("UPSI", "UPS Airlines", "air"),
    ("DLHA", "DHL Aviation", "air"),
    ("LCAG", "Lufthansa Cargo", "air"),
    ("IAOC", "IAG Cargo", "air"),
    ("ACGO", "Air Canada Cargo", "air"),
    ("QFCA", "Qantas Freight", "air"),
    # Rail
    ("BNSF", "BNSF Railway", "rail"),
    ("CSXI", "CSX Transportation", "rail"),
    ("UPRR", "Union Pacific Railroad", "rail"),
    ("CPRS", "Canadian Pacific Railway", "rail"),
]
