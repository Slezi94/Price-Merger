import pandas
from csvGenerator import csvGenerator
import datetime

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

# Attribútumok módosítása a nulla attribútomok esetében
def modify_attributes(ana_csv, lua_csv, do_csv, output):
    # Összefűzzük az árlistákat
    all_prices = pandas.concat([ana_csv, lua_csv, do_csv], ignore_index=True)

    # Csak azok a sorok, ahol attribútum 0

    zero_attr_rows = output[(output["Item.Attribute.0.Value"] == 0) & (output["PriceRule.Code"] != "ZeroPrice")]
    # Új sorokat ide gyűjtjük
    new_rows = []

    for _, row in zero_attr_rows.iterrows():
        ref = row["Item.Cleared.RefCode"]

        # Mely fájlokban szerepel az adott SKU és milyen attribute értékkel?
        matching_rows = all_prices[all_prices["sku"] == ref]

        if not matching_rows.empty:
            for _, match in matching_rows.iterrows():
                new_row = row.copy()
                new_row["Item.Attribute.0.Value"] = match["attribute"]
                new_rows.append(new_row)

    new_rows = pandas.DataFrame(data=new_rows)
    mask = ~zero_attr_rows["Item.Cleared.RefCode"].isin(new_rows["Item.Cleared.RefCode"])
    zero_attr_rows = zero_attr_rows[mask]
    zero_attr_rows = pandas.concat([zero_attr_rows, new_rows], ignore_index=True)

    return zero_attr_rows

# Stringek egységesítése

def change_str(codes, output):
    # Nyitási irány eltüntetése
    formatted_refCodes = []

    for row in codes:
        if isinstance(row, str):
            for suffix in ["_J", "_B", "_K"]:
                if (row == "AAFE60") or (row == "EFT50_68"):
                    row.strip(suffix)
                    row = row+"E"
                elif suffix in row:
                    row = row[:row.rfind(suffix)]

        formatted_refCodes.append(row)

    # Segéd oszlop létrehozása
    output["Item.Cleared.RefCode"] = formatted_refCodes
    output.to_csv("Output/output.csv", index=False)
    return output

# Árak beszúrása az output_fileba

def set_price(ana_csv, lua_csv, do_csv, output):
    # Anna árak hozzáfűzése az IS7 csv fájlhoz
    ana_merge = output.merge(
        ana_csv,
        left_on=["Item.Cleared.RefCode", "Item.Attribute.0.Value"],
        right_on=["sku", "attribute"],
        how="left"
    )

    output_file["ItemPrice"] = ana_merge["price"]

    # Antónia Laura Zille árak hozzáfűzése az IS7 csv fájlhoz
    lua_merge = output.merge(
        lua_csv,
        left_on=["Item.Cleared.RefCode", "Item.Attribute.0.Value"],
        right_on=["sku", "attribute"],
        how="left"
    )

    output_file["ItemPrice"] = output_file["ItemPrice"].fillna(lua_merge["price"])

    # Doroti árak hozzáfűzése az IS7 csv fájlhoz
    do_merge = output.merge(
        do_csv,
        left_on=["Item.Cleared.RefCode", "Item.Attribute.0.Value"],
        right_on=["sku", "attribute"],
        how="left"
    )

    output_file["ItemPrice"] = output_file["ItemPrice"].fillna(do_merge["price"])
    return output_file

# Árak None-ra állítása

output_file["ItemPrice"] = None
formatted_code = change_str(refCode, output_file)
zero_attr_df = modify_attributes(ana, lua, do, output_file)

# Azoknak a soroknak a törlése, amiknek az attribútumát megváltoztattuk
mask = ~output_file["Item.Cleared.RefCode"].isin(zero_attr_df["Item.Cleared.RefCode"])
output_file = output_file[mask]

#Összeillesztés

output_file = pandas.concat([zero_attr_df, output_file], join="inner", ignore_index=True)

item_price = set_price(ana, lua, do, output_file)

# Töltsük ki a hiányzó árakat nullával
output_file["ItemPrice"] = output_file["ItemPrice"].fillna(0)

# Ár egész számmá alakítása
output_file["ItemPrice"] = output_file["ItemPrice"].astype(int)

# Item.Cleared.RefCode oszlopot törölni
output_file = output_file.drop(columns=["Item.Cleared.RefCode"])

# CSV mentése
output_file.to_csv("Output/output.csv", index=False)

