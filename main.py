import pandas
from csvGenerator import csvGenerator
import datetime

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
attributes = output_file["Item.Attribute.0.Value"].to_list()

# Backup output file
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file.to_csv(f"Backup/output_backup_{timestamp}.csv", index=False)

formatted_refCode = []

for row in refCode:
    if isinstance(row, str):
        for suffix in ["_J", "_B", "_K"]:
            if suffix in row:
                row = row[:row.rfind(suffix)]
                break
    formatted_refCode.append(row)

output_file["Item.RefCode"] = formatted_refCode
output_file.to_csv("Output/output.csv", index=False)

output_file["ItemPrice"] = None

#Anna árak hozzáfűzése az IS7 csv fájlhoz
ana_merge = output_file.merge(
    ana,
    left_on=["Item.RefCode", "Item.Attribute.0.Value"],
    right_on=["sku", "attribute"],
    how="left"
)

output_file["ItemPrice"] = ana_merge["price"]

#Antónia Laura Zille árak hozzáfűzése az IS7 csv fájlhoz
lua_merge = output_file.merge(
    lua,
    left_on=["Item.RefCode", "Item.Attribute.0.Value"],
    right_on=["sku", "attribute"],
    how="left"
)

output_file["ItemPrice"] = output_file["ItemPrice"].fillna(lua_merge["price"])

#Doroti árak hozzáfűzése az IS7 csv fájlhoz
do_merge = output_file.merge(
    do,
    left_on=["Item.RefCode", "Item.Attribute.0.Value"],
    right_on=["sku", "attribute"],
    how="left"
)

output_file["ItemPrice"] = output_file["ItemPrice"].fillna(do_merge["price"])

# Töltsük ki a hiányzó árakat nullával
output_file["ItemPrice"] = output_file["ItemPrice"].fillna(0)

# Ár egész számmá alakítása
output_file["ItemPrice"] = output_file["ItemPrice"].astype(int)


# CSV mentése
output_file.to_csv("Output/output.csv", index=False)

