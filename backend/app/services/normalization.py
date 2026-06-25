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


MODEL_ALIASES = {
    "mazda cx5": "Mazda CX-5",
    "mazda cx-5": "Mazda CX-5",
    "mazda cx 5": "Mazda CX-5",
    "mazda cx3": "Mazda CX-3",
    "mazda cx-3": "Mazda CX-3",
    "mazda cx 3": "Mazda CX-3",
    "mazda cx30": "Mazda CX-30",
    "mazda cx-30": "Mazda CX-30",
    "mazda cx 30": "Mazda CX-30",
    "renault stepway": "Renault Stepway",
    "renault sandero": "Renault Sandero",
    "renault logan": "Renault Logan",
    "renault duster": "Renault Duster",
    "chevrolet onix": "Chevrolet Onix",
    "chevrolet onix plus": "Chevrolet Onix Plus",
    "chevrolet tracker": "Chevrolet Tracker",
    "chevrolet sail": "Chevrolet Sail",
    "chevrolet spark": "Chevrolet Spark",
    "chevrolet joy": "Chevrolet Joy",
    "chevrolet groove": "Chevrolet Groove",
    "toyota corolla": "Toyota Corolla",
    "toyota hilux": "Toyota Hilux",
    "toyota prado": "Toyota Prado",
    "toyota fortuner": "Toyota Fortuner",
    "nissan versa": "Nissan Versa",
    "nissan sentra": "Nissan Sentra",
    "nissan frontier": "Nissan Frontier",
    "nissan pathfinder": "Nissan Pathfinder",
    "nissan qashqai": "Nissan Qashqai",
    "hyundai accent": "Hyundai Accent",
    "hyundai elantra": "Hyundai Elantra",
    "hyundai tucson": "Hyundai Tucson",
    "hyundai i10": "Hyundai i10",
    "hyundai grand i10": "Hyundai Grand i10",
    "kia rio": "Kia Rio",
    "kia picanto": "Kia Picanto",
    "kia sportage": "Kia Sportage",
    "kia cerato": "Kia Cerato",
    "kia soul": "Kia Soul",
    "volkswagen gol": "Volkswagen Gol",
    "volkswagen polo": "Volkswagen Polo",
    "volkswagen vento": "Vento",
    "volkswagen t-cross": "Volkswagen T-Cross",
    "volkswagen taos": "Volkswagen Taos",
    "volkswagen nivus": "Volkswagen Nivus",
    "ford fiesta": "Ford Fiesta",
    "ford focus": "Ford Focus",
    "ford ranger": "Ford Ranger",
    "ford escape": "Ford Escape",
    "ford explorer": "Ford Explorer",
    "suzuki swift": "Suzuki Swift",
    "suzuki vitara": "Suzuki Vitara",
    "suzuki ignis": "Suzuki Ignis",
    "suzuki baleno": "Suzuki Baleno",
    "suzuki sx4": "Suzuki SX4",
    "honda civic": "Honda Civic",
    "honda cr-v": "Honda CR-V",
    "honda crv": "Honda CR-V",
    "honda accord": "Honda Accord",
}

YEAR_PATTERN = re.compile(r"\b(19[4-9]\d|20[0-2]\d)\b")
MILEAGE_PATTERN = re.compile(r"(\d[\d.,]*)\s*(km|kms|kilometraje)", re.IGNORECASE)
PRICE_PATTERN = re.compile(r"\$?\s?(\d[\d.,]*)")
VERSION_SEPARATOR = re.compile(r"\s+(l|lt|ltz|ls|lsz|gls|glx|sport|turbo|diesel|4x4|4wd|awd|full|base)\b", re.IGNORECASE)


def normalize_model(brand: str, raw_model: str) -> str:
    combined = f"{brand} {raw_model}".strip().lower()
    combined = re.sub(r"[^a-zA-Z0-9áéíóúñ\s-]", "", combined)
    combined = re.sub(r"\s+", " ", combined).strip()

    key = combined.lower()
    if key in MODEL_ALIASES:
        return MODEL_ALIASES[key]

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
