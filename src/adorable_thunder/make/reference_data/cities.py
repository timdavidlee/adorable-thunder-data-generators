# (city, state_or_province, country_code, postal_code)
CITIES = [
    # United States
    ("New York", "NY", "US", "10001"),
    ("Los Angeles", "CA", "US", "90001"),
    ("Chicago", "IL", "US", "60601"),
    ("Houston", "TX", "US", "77001"),
    ("San Francisco", "CA", "US", "94101"),
    ("Seattle", "WA", "US", "98101"),
    ("Boston", "MA", "US", "02101"),
    ("Atlanta", "GA", "US", "30301"),
    ("Miami", "FL", "US", "33101"),
    ("Dallas", "TX", "US", "75201"),
    ("Denver", "CO", "US", "80201"),
    ("Phoenix", "AZ", "US", "85001"),
    ("Minneapolis", "MN", "US", "55401"),
    ("Detroit", "MI", "US", "48201"),
    ("Portland", "OR", "US", "97201"),
    # Canada
    ("Toronto", "ON", "CA", "M5H 2N2"),
    ("Vancouver", "BC", "CA", "V6B 1A1"),
    ("Montreal", "QC", "CA", "H3A 1A1"),
    ("Calgary", "AB", "CA", "T2P 1A1"),
    # Mexico
    ("Mexico City", "CDMX", "MX", "06600"),
    ("Guadalajara", "JAL", "MX", "44100"),
    ("Monterrey", "NL", "MX", "64000"),
    # Brazil
    ("São Paulo", "SP", "BR", "01310-100"),
    ("Rio de Janeiro", "RJ", "BR", "20040-020"),
    ("Brasília", "DF", "BR", "70040-010"),
    ("Belo Horizonte", "MG", "BR", "30112-000"),
    # Argentina
    ("Buenos Aires", "Buenos Aires", "AR", "C1043"),
    ("Córdoba", "Córdoba", "AR", "X5000"),
    # Colombia
    ("Bogotá", "Cundinamarca", "CO", "110111"),
    ("Medellín", "Antioquia", "CO", "050001"),
    # Chile
    ("Santiago", "Metropolitan Region", "CL", "8320000"),
    # United Kingdom
    ("London", "England", "GB", "EC1A 1BB"),
    ("Manchester", "England", "GB", "M1 1AE"),
    ("Birmingham", "England", "GB", "B1 1BB"),
    ("Edinburgh", "Scotland", "GB", "EH1 1YZ"),
    ("Bristol", "England", "GB", "BS1 1AA"),
    # Germany
    ("Berlin", "Berlin", "DE", "10115"),
    ("Hamburg", "Hamburg", "DE", "20095"),
    ("Munich", "Bavaria", "DE", "80331"),
    ("Frankfurt", "Hesse", "DE", "60311"),
    ("Düsseldorf", "North Rhine-Westphalia", "DE", "40210"),
    # France
    ("Paris", "Île-de-France", "FR", "75001"),
    ("Lyon", "Auvergne-Rhône-Alpes", "FR", "69001"),
    ("Marseille", "Provence-Alpes-Côte d'Azur", "FR", "13001"),
    ("Toulouse", "Occitanie", "FR", "31000"),
    # Italy
    ("Milan", "Lombardy", "IT", "20121"),
    ("Rome", "Lazio", "IT", "00100"),
    ("Turin", "Piedmont", "IT", "10121"),
    # Spain
    ("Madrid", "Community of Madrid", "ES", "28001"),
    ("Barcelona", "Catalonia", "ES", "08001"),
    ("Valencia", "Valencian Community", "ES", "46001"),
    # Netherlands
    ("Amsterdam", "North Holland", "NL", "1011 AB"),
    ("Rotterdam", "South Holland", "NL", "3011 AA"),
    ("The Hague", "South Holland", "NL", "2511 AA"),
    # Switzerland
    ("Zurich", "Zurich", "CH", "8001"),
    ("Geneva", "Geneva", "CH", "1201"),
    ("Basel", "Basel-City", "CH", "4001"),
    # Sweden
    ("Stockholm", "Stockholm County", "SE", "111 20"),
    ("Gothenburg", "Västra Götaland", "SE", "411 01"),
    # Poland
    ("Warsaw", "Masovian", "PL", "00-001"),
    ("Kraków", "Lesser Poland", "PL", "30-001"),
    ("Wrocław", "Lower Silesian", "PL", "50-001"),
    # Belgium
    ("Brussels", "Brussels-Capital", "BE", "1000"),
    ("Antwerp", "Antwerp", "BE", "2000"),
    # Norway
    ("Oslo", "Oslo", "NO", "0150"),
    # Denmark
    ("Copenhagen", "Capital Region", "DK", "1000"),
    # Austria
    ("Vienna", "Vienna", "AT", "1010"),
    # Finland
    ("Helsinki", "Uusimaa", "FI", "00100"),
    # Portugal
    ("Lisbon", "Lisbon", "PT", "1100-001"),
    ("Porto", "Norte", "PT", "4000-001"),
    # Czech Republic
    ("Prague", "Prague", "CZ", "110 00"),
    # Romania
    ("Bucharest", "Ilfov", "RO", "010011"),
    # Hungary
    ("Budapest", "Central Hungary", "HU", "1051"),
    # Russia
    ("Moscow", "Moscow", "RU", "101000"),
    ("Saint Petersburg", "Saint Petersburg", "RU", "190000"),
    # Turkey
    ("Istanbul", "Istanbul", "TR", "34000"),
    ("Ankara", "Ankara", "TR", "06010"),
    # Israel
    ("Tel Aviv", "Tel Aviv District", "IL", "6100001"),
    # Saudi Arabia
    ("Riyadh", "Riyadh Province", "SA", "11564"),
    ("Jeddah", "Makkah Province", "SA", "21411"),
    # UAE
    ("Dubai", "Dubai", "AE", "00000"),
    ("Abu Dhabi", "Abu Dhabi", "AE", "00000"),
    # South Africa
    ("Johannesburg", "Gauteng", "ZA", "2000"),
    ("Cape Town", "Western Cape", "ZA", "8001"),
    ("Durban", "KwaZulu-Natal", "ZA", "4001"),
    # Nigeria
    ("Lagos", "Lagos State", "NG", "100001"),
    ("Abuja", "FCT", "NG", "900001"),
    # Egypt
    ("Cairo", "Cairo Governorate", "EG", "11511"),
    ("Alexandria", "Alexandria Governorate", "EG", "21500"),
    # Kenya
    ("Nairobi", "Nairobi County", "KE", "00100"),
    # India
    ("Mumbai", "Maharashtra", "IN", "400001"),
    ("Delhi", "Delhi", "IN", "110001"),
    ("Bangalore", "Karnataka", "IN", "560001"),
    ("Chennai", "Tamil Nadu", "IN", "600001"),
    ("Hyderabad", "Telangana", "IN", "500001"),
    ("Pune", "Maharashtra", "IN", "411001"),
    # China
    ("Shanghai", "Shanghai", "CN", "200001"),
    ("Beijing", "Beijing", "CN", "100001"),
    ("Shenzhen", "Guangdong", "CN", "518001"),
    ("Guangzhou", "Guangdong", "CN", "510001"),
    ("Chengdu", "Sichuan", "CN", "610001"),
    ("Hangzhou", "Zhejiang", "CN", "310001"),
    # Japan
    ("Tokyo", "Tokyo", "JP", "100-0001"),
    ("Osaka", "Osaka", "JP", "530-0001"),
    ("Nagoya", "Aichi", "JP", "460-0001"),
    ("Yokohama", "Kanagawa", "JP", "220-0001"),
    # South Korea
    ("Seoul", "Seoul", "KR", "04524"),
    ("Busan", "Busan", "KR", "48958"),
    ("Incheon", "Incheon", "KR", "22320"),
    # Taiwan
    ("Taipei", "Taipei", "TW", "100"),
    ("Kaohsiung", "Kaohsiung", "TW", "800"),
    # Singapore
    ("Singapore", "", "SG", "018989"),
    # Malaysia
    ("Kuala Lumpur", "Federal Territory", "MY", "50000"),
    ("Penang", "Penang", "MY", "10000"),
    # Thailand
    ("Bangkok", "Bangkok", "TH", "10100"),
    ("Chiang Mai", "Chiang Mai", "TH", "50000"),
    # Indonesia
    ("Jakarta", "DKI Jakarta", "ID", "10110"),
    ("Surabaya", "East Java", "ID", "60111"),
    # Vietnam
    ("Ho Chi Minh City", "Ho Chi Minh", "VN", "700000"),
    ("Hanoi", "Hanoi", "VN", "100000"),
    # Philippines
    ("Manila", "Metro Manila", "PH", "1000"),
    ("Cebu City", "Cebu", "PH", "6000"),
    # Pakistan
    ("Karachi", "Sindh", "PK", "74200"),
    ("Lahore", "Punjab", "PK", "54000"),
    # Australia
    ("Sydney", "New South Wales", "AU", "2000"),
    ("Melbourne", "Victoria", "AU", "3000"),
    ("Brisbane", "Queensland", "AU", "4000"),
    ("Perth", "Western Australia", "AU", "6000"),
    # New Zealand
    ("Auckland", "Auckland", "NZ", "1010"),
    ("Wellington", "Wellington", "NZ", "6011"),
]
