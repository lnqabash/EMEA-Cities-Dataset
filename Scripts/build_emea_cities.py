import io, os, zipfile, requests, pandas as pd

# -------- CONFIG --------
GEONAMES_ZIP_URL = "https://download.geonames.org/export/dump/cities500.zip"
COUNTRY_INFO_URL = "https://download.geonames.org/export/dump/countryInfo.txt"
EMEA_COUNTRY_LIST_FILE = "Data/emea_countries.txt"
OUT_CSV = "Outputs/emea_country_major_cities.csv"
OUT_XLSX = "Outputs/emea_country_major_cities.xlsx"
TOP_N_CITIES_PER_COUNTRY = 20   # Top N cities per country by population
MIN_POPULATION = 50000          # optional: filter out small towns
# ------------------------

def download_bytes(url):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    return io.BytesIO(r.content)

def load_countryinfo(url):
    r = requests.get(url)
    r.raise_for_status()
    mapping = {}
    for line in r.text.splitlines():
        if not line or line.startswith("#"): 
            continue
        parts = line.split("\t")
        code = parts[0]
        name = parts[4]
        mapping[code] = name
    return mapping

def read_emea_list(path):
    with open(path, "r", encoding="utf-8") as f:
        names = [line.strip() for line in f if line.strip()]
    return set([n.lower() for n in names])

def extract_major_cities(zip_bytes, country_map, emea_lower_set, top_n=10, min_pop=50000):
    with zipfile.ZipFile(zip_bytes) as z:
        member = None
        for name in z.namelist():
            if name.lower().startswith("cities") and name.lower().endswith(".txt"):
                member = name
                break
        if member is None:
            member = z.namelist()[0]
        with z.open(member) as fh:
            cols = [
                "geonameid","name","asciiname","alternatenames","latitude","longitude",
                "feature_class","feature_code","country_code","cc2","admin1","admin2","admin3","admin4",
                "population","elevation","dem","timezone","modification_date"
            ]
            df = pd.read_csv(fh, sep="\t", names=cols, dtype={"country_code": str}, low_memory=False)
    df["country_name"] = df["country_code"].map(country_map).fillna(df["country_code"])
    df["country_name_lc"] = df["country_name"].str.lower()
    df["population"] = pd.to_numeric(df["population"], errors="coerce").fillna(0).astype(int)
    df = df[df["country_name_lc"].isin(emea_lower_set) & (df["population"] >= min_pop)]
    
    # Keep top N cities per country
    df_major = df.sort_values(["country_name","population"], ascending=[True, False])
    df_top_n = df_major.groupby("country_name").head(top_n).copy()
    
    out_cols = ["geonameid","name","asciiname","country_code","country_name","admin1","latitude","longitude","population","timezone"]
    return df_top_n[out_cols]

def main():
    emea_set = read_emea_list(EMEA_COUNTRY_LIST_FILE)
    country_map = load_countryinfo(COUNTRY_INFO_URL)
    zip_bytes = download_bytes(GEONAMES_ZIP_URL)
    df_top = extract_major_cities(zip_bytes, country_map, emea_set, TOP_N_CITIES_PER_COUNTRY, MIN_POPULATION)
    print(f"Total major cities found: {len(df_top)}")
    
    df_top.to_csv(OUT_CSV, index=False, encoding="utf-8")
    print("CSV saved:", OUT_CSV)
    try:
        df_top.to_excel(OUT_XLSX, index=False)
        print("Excel saved:", OUT_XLSX)
    except Exception as e:
        print("Error writing Excel (openpyxl required).", e)

if __name__ == "__main__":
    main()

