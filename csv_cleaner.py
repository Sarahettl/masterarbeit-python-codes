import pandas as pd
import csv
import sys

def transform_csv(file_path, output_path=None):
    # Versuche robustes Einlesen mit dem Python-Engine
    try:
        df_raw = pd.read_csv(
            file_path,
            sep=';',
            engine='python',
            quoting=csv.QUOTE_MINIMAL,
            on_bad_lines='skip',
            encoding='utf-8',
            dtype=str,  # alles als Text, um robust zu bleiben
            keep_default_na=False  # wichtig: "N/A" NICHT als NaN interpretieren
        )
    except Exception as e:
        print(f"Fehler beim Einlesen der Datei: {e}")
        sys.exit(1)

    df = df_raw.copy()

    # Benutzer anonymisieren mit fortlaufender ID
    if 'User' in df.columns:
        user_mapping = {name: f"id_{idx+1}" for idx, name in enumerate(df['User'].unique())}
        df['user_id_anonym'] = df['User'].map(user_mapping)


    # Neue Spalten aus "Average Rating (N Reviews)"
    if 'Average Rating (N Reviews)' in df.columns:
        extracted = df['Average Rating (N Reviews)'].str.extract(r'([\d,]+)\s*\(([^)]+)\)')
        df['Average Rating'] = extracted[0].str.replace(',', '.', regex=False)
        df['N Reviews'] = extracted[1].str.replace('.', '', regex=False)
        df['Average Rating'] = pd.to_numeric(df['Average Rating'], errors='coerce')
        df['N Reviews'] = pd.to_numeric(df['N Reviews'], errors='coerce')

    # City und Country trennen
    if 'City, Country' in df.columns:
        df[['City', 'Country']] = df['City, Country'].str.split(',', n=1, expand=True)
        df['City'] = df['City'].str.strip()
        df['Country'] = df['Country'].str.strip()

    # Datum aufsplitten
    if 'Date of Visit' in df.columns:
        df[['Month of Visit', 'Year of Visit']] = df['Date of Visit'].str.extract(r'(\d{2})/(\d{4})')

    # Alte Spalten entfernen (falls vorhanden)
    for col in ['Average Rating (N Reviews)', 'City, Country', 'Date of Visit']:
        if col in df.columns:
            df.drop(columns=col, inplace=True)

    # Optional speichern
    if output_path:
        df.to_csv(output_path, index=False)

    return df

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Bitte gib den Pfad zur CSV-Datei an.")
        print("Beispiel: python3 csv_cleaner.py Trialbatch.csv Trialbatch_cleaned.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    df = transform_csv(input_file, output_file)
    print(f"Transformation abgeschlossen. Zeilen: {len(df)}")
    if output_file:
        print(f"Gespeichert als: {output_file}")
