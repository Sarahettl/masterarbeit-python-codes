import pandas as pd

# CSV einlesen mit ; als Separator
df = pd.read_csv("Trialbatch_cleaned.csv", sep=",", on_bad_lines='skip')

# Spaltennamen aufräumen
df.columns = df.columns.str.strip()

# Prüfen, ob Spalten da sind
print("Spaltennamen:", df.columns.tolist())

# Nur gewünschte Spalten auswählen
df_subset = df[['Reviewed Location Name', 'City', 'Country']]

# Duplikate entfernen
unique_places = df_subset.drop_duplicates()

# Ausgabe & speichern
print(unique_places)
unique_places.to_csv("unique_tripadvisor_places_Trialbatch.csv", index=False)
