from typing import NamedTuple


class City(NamedTuple):
    city: str
    state_province: str
    country_code: str
    postal_code: str


CITIES: list[City] = [
    # United States
    City("New York", "NY", "US", "10001"),
    City("Los Angeles", "CA", "US", "90001"),
    City("Chicago", "IL", "US", "60601"),
    City("Houston", "TX", "US", "77001"),
    City("San Francisco", "CA", "US", "94101"),
    City("Seattle", "WA", "US", "98101"),
    City("Boston", "MA", "US", "02101"),
    City("Atlanta", "GA", "US", "30301"),
    City("Miami", "FL", "US", "33101"),
    City("Dallas", "TX", "US", "75201"),
    City("Denver", "CO", "US", "80201"),
    City("Phoenix", "AZ", "US", "85001"),
    City("Minneapolis", "MN", "US", "55401"),
    City("Detroit", "MI", "US", "48201"),
    City("Portland", "OR", "US", "97201"),
    # Canada
    City("Toronto", "ON", "CA", "M5H 2N2"),
    City("Vancouver", "BC", "CA", "V6B 1A1"),
    City("Montreal", "QC", "CA", "H3A 1A1"),
    City("Calgary", "AB", "CA", "T2P 1A1"),
    # Mexico
    City("Mexico City", "CDMX", "MX", "06600"),
    City("Guadalajara", "JAL", "MX", "44100"),
    City("Monterrey", "NL", "MX", "64000"),
    # Brazil
    City("São Paulo", "SP", "BR", "01310-100"),
    City("Rio de Janeiro", "RJ", "BR", "20040-020"),
    City("Brasília", "DF", "BR", "70040-010"),
    City("Belo Horizonte", "MG", "BR", "30112-000"),
    # Argentina
    City("Buenos Aires", "Buenos Aires", "AR", "C1043"),
    City("Córdoba", "Córdoba", "AR", "X5000"),
    # Colombia
    City("Bogotá", "Cundinamarca", "CO", "110111"),
    City("Medellín", "Antioquia", "CO", "050001"),
    # Chile
    City("Santiago", "Metropolitan Region", "CL", "8320000"),
    # United Kingdom
    City("London", "England", "GB", "EC1A 1BB"),
    City("Manchester", "England", "GB", "M1 1AE"),
    City("Birmingham", "England", "GB", "B1 1BB"),
    City("Edinburgh", "Scotland", "GB", "EH1 1YZ"),
    City("Bristol", "England", "GB", "BS1 1AA"),
    # Germany
    City("Berlin", "Berlin", "DE", "10115"),
    City("Hamburg", "Hamburg", "DE", "20095"),
    City("Munich", "Bavaria", "DE", "80331"),
    City("Frankfurt", "Hesse", "DE", "60311"),
    City("Düsseldorf", "North Rhine-Westphalia", "DE", "40210"),
    # France
    City("Paris", "Île-de-France", "FR", "75001"),
    City("Lyon", "Auvergne-Rhône-Alpes", "FR", "69001"),
    City("Marseille", "Provence-Alpes-Côte d'Azur", "FR", "13001"),
    City("Toulouse", "Occitanie", "FR", "31000"),
    # Italy
    City("Milan", "Lombardy", "IT", "20121"),
    City("Rome", "Lazio", "IT", "00100"),
    City("Turin", "Piedmont", "IT", "10121"),
    # Spain
    City("Madrid", "Community of Madrid", "ES", "28001"),
    City("Barcelona", "Catalonia", "ES", "08001"),
    City("Valencia", "Valencian Community", "ES", "46001"),
    # Netherlands
    City("Amsterdam", "North Holland", "NL", "1011 AB"),
    City("Rotterdam", "South Holland", "NL", "3011 AA"),
    City("The Hague", "South Holland", "NL", "2511 AA"),
    # Switzerland
    City("Zurich", "Zurich", "CH", "8001"),
    City("Geneva", "Geneva", "CH", "1201"),
    City("Basel", "Basel-City", "CH", "4001"),
    # Sweden
    City("Stockholm", "Stockholm County", "SE", "111 20"),
    City("Gothenburg", "Västra Götaland", "SE", "411 01"),
    # Poland
    City("Warsaw", "Masovian", "PL", "00-001"),
    City("Kraków", "Lesser Poland", "PL", "30-001"),
    City("Wrocław", "Lower Silesian", "PL", "50-001"),
    # Belgium
    City("Brussels", "Brussels-Capital", "BE", "1000"),
    City("Antwerp", "Antwerp", "BE", "2000"),
    # Norway
    City("Oslo", "Oslo", "NO", "0150"),
    # Denmark
    City("Copenhagen", "Capital Region", "DK", "1000"),
    # Austria
    City("Vienna", "Vienna", "AT", "1010"),
    # Finland
    City("Helsinki", "Uusimaa", "FI", "00100"),
    # Portugal
    City("Lisbon", "Lisbon", "PT", "1100-001"),
    City("Porto", "Norte", "PT", "4000-001"),
    # Czech Republic
    City("Prague", "Prague", "CZ", "110 00"),
    # Romania
    City("Bucharest", "Ilfov", "RO", "010011"),
    # Hungary
    City("Budapest", "Central Hungary", "HU", "1051"),
    # Russia
    City("Moscow", "Moscow", "RU", "101000"),
    City("Saint Petersburg", "Saint Petersburg", "RU", "190000"),
    # Turkey
    City("Istanbul", "Istanbul", "TR", "34000"),
    City("Ankara", "Ankara", "TR", "06010"),
    # Israel
    City("Tel Aviv", "Tel Aviv District", "IL", "6100001"),
    # Saudi Arabia
    City("Riyadh", "Riyadh Province", "SA", "11564"),
    City("Jeddah", "Makkah Province", "SA", "21411"),
    # UAE
    City("Dubai", "Dubai", "AE", "00000"),
    City("Abu Dhabi", "Abu Dhabi", "AE", "00000"),
    # South Africa
    City("Johannesburg", "Gauteng", "ZA", "2000"),
    City("Cape Town", "Western Cape", "ZA", "8001"),
    City("Durban", "KwaZulu-Natal", "ZA", "4001"),
    # Nigeria
    City("Lagos", "Lagos State", "NG", "100001"),
    City("Abuja", "FCT", "NG", "900001"),
    # Egypt
    City("Cairo", "Cairo Governorate", "EG", "11511"),
    City("Alexandria", "Alexandria Governorate", "EG", "21500"),
    # Kenya
    City("Nairobi", "Nairobi County", "KE", "00100"),
    # India
    City("Mumbai", "Maharashtra", "IN", "400001"),
    City("Delhi", "Delhi", "IN", "110001"),
    City("Bangalore", "Karnataka", "IN", "560001"),
    City("Chennai", "Tamil Nadu", "IN", "600001"),
    City("Hyderabad", "Telangana", "IN", "500001"),
    City("Pune", "Maharashtra", "IN", "411001"),
    # China
    City("Shanghai", "Shanghai", "CN", "200001"),
    City("Beijing", "Beijing", "CN", "100001"),
    City("Shenzhen", "Guangdong", "CN", "518001"),
    City("Guangzhou", "Guangdong", "CN", "510001"),
    City("Chengdu", "Sichuan", "CN", "610001"),
    City("Hangzhou", "Zhejiang", "CN", "310001"),
    # Japan
    City("Tokyo", "Tokyo", "JP", "100-0001"),
    City("Osaka", "Osaka", "JP", "530-0001"),
    City("Nagoya", "Aichi", "JP", "460-0001"),
    City("Yokohama", "Kanagawa", "JP", "220-0001"),
    # South Korea
    City("Seoul", "Seoul", "KR", "04524"),
    City("Busan", "Busan", "KR", "48958"),
    City("Incheon", "Incheon", "KR", "22320"),
    # Taiwan
    City("Taipei", "Taipei", "TW", "100"),
    City("Kaohsiung", "Kaohsiung", "TW", "800"),
    # Singapore
    City("Singapore", "", "SG", "018989"),
    # Malaysia
    City("Kuala Lumpur", "Federal Territory", "MY", "50000"),
    City("Penang", "Penang", "MY", "10000"),
    # Thailand
    City("Bangkok", "Bangkok", "TH", "10100"),
    City("Chiang Mai", "Chiang Mai", "TH", "50000"),
    # Indonesia
    City("Jakarta", "DKI Jakarta", "ID", "10110"),
    City("Surabaya", "East Java", "ID", "60111"),
    # Vietnam
    City("Ho Chi Minh City", "Ho Chi Minh", "VN", "700000"),
    City("Hanoi", "Hanoi", "VN", "100000"),
    # Philippines
    City("Manila", "Metro Manila", "PH", "1000"),
    City("Cebu City", "Cebu", "PH", "6000"),
    # Pakistan
    City("Karachi", "Sindh", "PK", "74200"),
    City("Lahore", "Punjab", "PK", "54000"),
    # Australia
    City("Sydney", "New South Wales", "AU", "2000"),
    City("Melbourne", "Victoria", "AU", "3000"),
    City("Brisbane", "Queensland", "AU", "4000"),
    City("Perth", "Western Australia", "AU", "6000"),
    # New Zealand
    City("Auckland", "Auckland", "NZ", "1010"),
    City("Wellington", "Wellington", "NZ", "6011"),
]
