from typing import NamedTuple


class Carrier(NamedTuple):
    scac_code: str
    carrier_name: str
    primary_mode: str


# SCAC = Standard Carrier Alpha Code (4-letter industry identifier)
CARRIERS: list[Carrier] = [
    # Road — North America
    Carrier("JBHT", "J.B. Hunt Transport Services", "road"),
    Carrier("ODFL", "Old Dominion Freight Line", "road"),
    Carrier("SAIA", "Saia Inc.", "road"),
    Carrier("RLCA", "R+L Carriers", "road"),
    Carrier("ABFS", "ABF Freight System", "road"),
    Carrier("FXFE", "FedEx Freight", "road"),
    Carrier("UPGF", "UPS Freight", "road"),
    Carrier("EXLA", "Estes Express Lines", "road"),
    # Road — International / Europe
    Carrier("DHLF", "DHL Freight", "road"),
    Carrier("DSVS", "DSV Road", "road"),
    Carrier("DBSC", "DB Schenker Road", "road"),
    Carrier("KNET", "Kuehne+Nagel Road", "road"),
    # Parcel / Express
    Carrier("FDXG", "FedEx Ground", "parcel"),
    Carrier("UPSN", "UPS", "parcel"),
    Carrier("USPS", "USPS", "parcel"),
    Carrier("DHLE", "DHL Express", "parcel"),
    Carrier("TNTE", "TNT Express", "parcel"),
    Carrier("DPWG", "DPD", "parcel"),
    # Ocean
    Carrier("MAEU", "Maersk", "ocean"),
    Carrier("MSCU", "MSC", "ocean"),
    Carrier("COSU", "COSCO Shipping", "ocean"),
    Carrier("HLCU", "Hapag-Lloyd", "ocean"),
    Carrier("EGLV", "Evergreen", "ocean"),
    Carrier("CMDU", "CMA CGM", "ocean"),
    Carrier("ONEY", "ONE (Ocean Network Express)", "ocean"),
    Carrier("YMLU", "Yang Ming", "ocean"),
    # Air Freight
    Carrier("FXAI", "FedEx Express", "air"),
    Carrier("UPSI", "UPS Airlines", "air"),
    Carrier("DLHA", "DHL Aviation", "air"),
    Carrier("LCAG", "Lufthansa Cargo", "air"),
    Carrier("IAOC", "IAG Cargo", "air"),
    Carrier("ACGO", "Air Canada Cargo", "air"),
    Carrier("QFCA", "Qantas Freight", "air"),
    # Rail
    Carrier("BNSF", "BNSF Railway", "rail"),
    Carrier("CSXI", "CSX Transportation", "rail"),
    Carrier("UPRR", "Union Pacific Railroad", "rail"),
    Carrier("CPRS", "Canadian Pacific Railway", "rail"),
]
