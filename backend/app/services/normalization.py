import re

BRAND_ALIASES = {
    "chevrolet": "Chevrolet",
    "chevrlet": "Chevrolet",
    "chevy": "Chevrolet",
    "mazda": "Mazda",
    "renault": "Renault",
    "rnault": "Renault",
    "nissan": "Nissan",
    "nisan": "Nissan",
    "toyota": "Toyota",
    "toyta": "Toyota",
    "hyundai": "Hyundai",
    "hiunday": "Hyundai",
    "kia": "Kia",
    "fiat": "Fiat",
    "volkswagen": "Volkswagen",
    "vw": "Volkswagen",
    "ford": "Ford",
    "mercedes": "Mercedes-Benz",
    "mercedes benz": "Mercedes-Benz",
    "bmw": "BMW",
    "audi": "Audi",
    "suzuki": "Suzuki",
    "suzuky": "Suzuki",
    "honda": "Honda",
    "mitsubishi": "Mitsubishi",
    "mitsubish": "Mitsubishi",
    "subaru": "Subaru",
    "jim": "JMC",
    "jac": "JAC",
    "great wall": "Great Wall",
    "chery": "Chery",
    "changan": "Changan",
    "dongfeng": "DFSK",
    "dfsk": "DFSK",
}


def normalize_brand(raw: str) -> str:
    cleaned = re.sub(r"[^a-zA-Záéíóúñ\s]", "", raw).strip().lower()
    return BRAND_ALIASES.get(cleaned, raw.strip().title())


KNOWN_MODELS = {
    "Mazda": {
        "2": "2", "3": "3", "5": "5", "6": "6", "626": "626", "323": "323",
        "cx-3": "CX-3", "cx3": "CX-3", "cx-5": "CX-5", "cx5": "CX-5",
        "cx-30": "CX-30", "cx30": "CX-30", "cx-50": "CX-50", "cx50": "CX-50",
        "cx-9": "CX-9", "cx9": "CX-9", "cx-90": "CX-90", "cx90": "CX-90",
        "mx-5": "MX-5", "mx5": "MX-5", "miata": "Miata", "bt-50": "BT-50", "bt50": "BT-50"
    },
    "Chevrolet": {
        "spark": "Spark", "beat": "Beat", "sail": "Sail", "onix": "Onix", "cruze": "Cruze",
        "tracker": "Tracker", "captiva": "Captiva", "trailblazer": "Trailblazer", "tahoe": "Tahoe",
        "suburban": "Suburban", "joy": "Joy", "groove": "Groove", "traverse": "Traverse",
        "camaro": "Camaro", "equinox": "Equinox", "colorado": "Colorado", "d-max": "D-Max",
        "dmax": "D-Max", "aveo": "Aveo", "optra": "Optra", "cobalt": "Cobalt", "corsa": "Corsa",
        "n300": "N300", "n400": "N400"
    },
    "Renault": {
        "clio": "Clio", "sandero": "Sandero", "logan": "Logan", "stepway": "Stepway",
        "duster": "Duster", "koleos": "Koleos", "kwid": "Kwid", "megane": "Megane",
        "scenic": "Scenic", "twingo": "Twingo", "symbol": "Symbol", "fluence": "Fluence",
        "captur": "Captur", "alaskan": "Alaskan", "oroch": "Oroch"
    },
    "Toyota": {
        "corolla": "Corolla", "yaris": "Yaris", "hilux": "Hilux", "prado": "Prado",
        "fortuner": "Fortuner", "4runner": "4Runner", "land cruiser": "Land Cruiser",
        "lc300": "Land Cruiser", "rav4": "Rav4", "rav 4": "Rav4", "rush": "Rush",
        "sw4": "Sw4", "tundra": "Tundra", "tacoma": "Tacoma", "fj cruiser": "Fj Cruiser",
        "lc200": "Land Cruiser"
    },
    "Nissan": {
        "march": "March", "versa": "Versa", "sentra": "Sentra", "tiida": "Tiida",
        "kicks": "Kicks", "qashqai": "Qashqai", "x-trail": "X-Trail", "xtrail": "X-Trail",
        "frontier": "Frontier", "pathfinder": "Pathfinder", "murano": "Murano", "patrol": "Patrol"
    },
    "Kia": {
        "picanto": "Picanto", "rio": "Rio", "soluto": "Soluto", "cerato": "Cerato",
        "sportage": "Sportage", "sorento": "Sorento", "sonet": "Sonet", "seltos": "Seltos",
        "stonic": "Stonic", "niro": "Niro", "soul": "Soul"
    },
    "Hyundai": {
        "i10": "i10", "grand i10": "i10", "accent": "Accent", "elantra": "Elantra",
        "tucson": "Tucson", "santa fe": "Santa Fe", "creta": "Creta", "hb20": "HB20",
        "getz": "Getz", "i35": "i35", "i25": "i25"
    },
    "Ford": {
        "fiesta": "Fiesta", "focus": "Focus", "fusion": "Fusion", "ecosport": "Ecosport",
        "escape": "Escape", "edge": "Edge", "explorer": "Explorer", "expedition": "Expedition",
        "ranger": "Ranger", "f-150": "F-150", "f150": "F-150", "mustang": "Mustang"
    },
    "Suzuki": {
        "swift": "Swift", "dzire": "Dzire", "alto": "Alto", "baleno": "Baleno",
        "vitara": "Vitara", "grand vitara": "Grand Vitara", "jimny": "Jimny",
        "s-cross": "S-Cross", "scross": "S-Cross", "ignis": "Ignis", "ertiga": "Ertiga"
    },
    "Volkswagen": {
        "gol": "Gol", "voyage": "Voyage", "polo": "Polo", "virtus": "Virtus",
        "jetta": "Jetta", "golf": "Golf", "t-cross": "T-Cross", "tcross": "T-Cross",
        "nivus": "Nivus", "taos": "Taos", "tiguan": "Tiguan", "amarok": "Amarok",
        "bora": "Bora", "vento": "Vento"
    }
}

YEAR_PATTERN = re.compile(r"\b(19[4-9]\d|20[0-2]\d)\b")
MILEAGE_PATTERN = re.compile(r"(\d[\d.,]*)\s*(km|kms|kilometraje)", re.IGNORECASE)
PRICE_PATTERN = re.compile(r"\$?\s?(\d[\d.,]*)")
VERSION_SEPARATOR = re.compile(r"\s+(l|lt|ltz|ls|lsz|gls|glx|sport|turbo|diesel|4x4|4wd|awd|full|base)\b", re.IGNORECASE)


def normalize_model(brand: str, raw_model: str) -> str:
    brand_norm = brand.strip().title()
    model_lower = raw_model.strip().lower()

    # 1. Limpiar caracteres especiales
    model_clean = re.sub(r"[^a-zA-Z0-9áéíóúñ\s-]", "", model_lower)
    model_clean = re.sub(r"\s+", " ", model_clean).strip()

    # 2. Comprobar si coincide con algun modelo base conocido de esta marca
    if brand_norm in KNOWN_MODELS:
        # Ordenamos las claves de mayor a menor longitud
        sorted_keys = sorted(KNOWN_MODELS[brand_norm].keys(), key=len, reverse=True)
        for key in sorted_keys:
            pattern = rf"\b{re.escape(key)}\b"
            if re.search(pattern, model_clean):
                return KNOWN_MODELS[brand_norm][key]

    # 3. Si no coincide con ninguno conocido, aplicar heuristica del primer token
    words = model_clean.split()
    if words:
        # Si la primera palabra es comun de modelo compuesto
        if len(words) > 1 and words[0] in ["clase", "serie", "grand", "land", "new"]:
            return f"{words[0].title()} {words[1].title()}"
        return words[0].title()

    return raw_model.strip().title()


def extract_year(text: str) -> int | None:
    matches = YEAR_PATTERN.findall(text)
    if matches:
        return int(matches[0])
    return None


def extract_mileage(text: str) -> int | None:
    match = MILEAGE_PATTERN.search(text)
    if match:
        cleaned = match.group(1).replace(".", "").replace(",", "")
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None


def extract_price(text: str) -> float | None:
    match = PRICE_PATTERN.search(text)
    if match:
        cleaned = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None
