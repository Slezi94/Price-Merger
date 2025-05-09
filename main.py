import pandas
from csvGenerator import csvGenerator
import datetime

#def insert_rows(pandas, output_file, ana_csv, lua_csv, do_csv):


# CSV fájlok generálása Inputból
generator = csvGenerator()
generator.ana_csv()
generator.lau_csv()
generator.do_csv()

# Input mappa
ana = pandas.read_csv("Input/ana.csv")
lua = pandas.read_csv("Input/lua.csv")
do = pandas.read_csv("Input/do.csv")

# Output mappa
output_file = pandas.read_csv("Output/output.csv")
refCode = output_file["Item.RefCode"].to_list()
output_file["Item.Attribute.0.Value"] = output_file["Item.Attribute.0.Value"].fillna(0).astype(int)


# Backup output fájl
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file.to_csv(f"Backup/output_backup_{timestamp}.csv", index=False)

# Nyitási irány eltüntetése
formatted_refCode = []

for row in refCode:
    if isinstance(row, str):
        for suffix in ["_J", "_B", "_K"]:
            if suffix in row:
                row = row[:row.rfind(suffix)]
                break
    formatted_refCode.append(row)

# Segéd oszlop létrehozása
output_file["Item.Cleared.RefCode"] = formatted_refCode
output_file.to_csv("Output/output.csv", index=False)

output_file["ItemPrice"] = None

#TODO:A 0-ás attribute-ok nál felvenni ugyan azokat a sorokat, megváltoztatni az attribútumát és felvenni az árát


#insert_rows(pandas, output_file, ana, lua, do)
# Összefűzzük az árlistákat
all_prices = pandas.concat([ana, lua, do], ignore_index=True)

# Csak azok a sorok, ahol attribútum 0

zero_attr_rows = output_file[output_file["Item.Attribute.0.Value"] == 0]

# Új sorokat ide gyűjtjük
new_rows = []

for _, row in zero_attr_rows.iterrows():
    ref = row["Item.Cleared.RefCode"]

    # Mely fájlokban szerepel az adott SKU és milyen attribute értékkel?
    matching_rows = all_prices[all_prices["sku"] == ref]

    if not matching_rows.empty:
        print(matching_rows)
        for _, match in matching_rows.iterrows():
            new_row = row.copy()
            new_row["Item.Attribute.0.Value"] = match["attribute"]
            new_rows.append(new_row)

# Töröljük a 0 attribútumos sorokat
mask = ~((output_file["Item.Attribute.0.Value"] == 0) & (output_file["PriceRule.Code"] != "ZeroPrice"))

output_file = output_file[mask]

# Új sorok hozzáadása
output_file = pandas.concat([output_file, pandas.DataFrame(new_rows)], ignore_index=True)
output_file.to_csv("Output/output.csv", index=False)
#print("sd")

#Anna árak hozzáfűzése az IS7 csv fájlhoz
ana_merge = output_file.merge(
    ana,
    left_on=["Item.Cleared.RefCode", "Item.Attribute.0.Value"],
    right_on=["sku", "attribute"],
    how="left"
)

output_file["ItemPrice"] = ana_merge["price"]

#Antónia Laura Zille árak hozzáfűzése az IS7 csv fájlhoz
lua_merge = output_file.merge(
    lua,
    left_on=["Item.Cleared.RefCode", "Item.Attribute.0.Value"],
    right_on=["sku", "attribute"],
    how="left"
)

output_file["ItemPrice"] = output_file["ItemPrice"].fillna(lua_merge["price"])

#Doroti árak hozzáfűzése az IS7 csv fájlhoz
do_merge = output_file.merge(
    do,
    left_on=["Item.Cleared.RefCode", "Item.Attribute.0.Value"],
    right_on=["sku", "attribute"],
    how="left"
)

output_file["ItemPrice"] = output_file["ItemPrice"].fillna(do_merge["price"])

# Töltsük ki a hiányzó árakat nullával
output_file["ItemPrice"] = output_file["ItemPrice"].fillna(0)

# Ár egész számmá alakítása
output_file["ItemPrice"] = output_file["ItemPrice"].astype(int)

#TODO: Segéd oszlopot törölni

# CSV mentése
output_file.to_csv("Output/output.csv", index=False)

