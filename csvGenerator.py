import xlwings as xw
import pandas

ANA_ATTRIBUTE = 1
LUA_ATTRIBUTE = [2, 3, 4, 5]
DO_ATTRIBUTE = 7


class csvGenerator:
    def __init__(self):
        self.ana_sheet = xw.Book("Input/Input.xlsx").sheets[0]
        self.lua_sheet = xw.Book("Input/Input.xlsx").sheets[1]
        self.do_sheet = xw.Book("Input/Input.xlsx").sheets[2]
        self.sku_list = []
        self.price_list = []

    def ana_csv(self):
        last_row = self.ana_sheet.range(f"F{str(self.ana_sheet.cells.last_cell.row)}").end('up').row
        self.sku_list = self.ana_sheet.range(f"B2:B{last_row}").value
        price = self.ana_sheet.range(f"F2:F{last_row}").value
        self.price_list = []

        for row in price:
            if type(row) == float:
                row = int(row)
            else:
                row = 0
            self.price_list.append(int(row))

        ana_dict = {
            "sku": self.sku_list,
            "price": self.price_list,
            "attribute": 1
        }
        ana_data = pandas.DataFrame(ana_dict)
        ana_data.to_csv("Input/ana.csv")

    def lau_csv(self):
        last_row = self.lua_sheet.range(f"F{self.lua_sheet.cells.last_cell.row}").end('up').row
        raw_skus = self.lua_sheet.range(f"B2:B{last_row}").value
        raw_prices = self.lua_sheet.range(f"F2:F{last_row}").value

        self.sku_list = []
        self.price_list = []
        attribute_list = []

        for sku, price in zip(raw_skus, raw_prices):
            if sku is None:
                continue

            cleaned_sku = sku.replace("Ü", "U")

            price = int(price) if isinstance(price, float) else 0

            if sku in ["FÜ80F", "FZN80"]:
                self.sku_list.append(cleaned_sku)
                self.price_list.append(price)
                attribute_list.append(5)
            else:
                for attr in range(2, 6):
                    self.sku_list.append(cleaned_sku)
                    self.price_list.append(price)
                    attribute_list.append(attr)

        lua_dict = pandas.DataFrame({
            "sku": self.sku_list,
            "price": self.price_list,
            "attribute": attribute_list
        })

        lua_data = pandas.DataFrame(lua_dict)
        lua_data.to_csv("Input/lua.csv")

    def do_csv(self):
        last_row = self.do_sheet.range(f"F{str(self.do_sheet.cells.last_cell.row)}").end('up').row
        raw_skus = self.do_sheet.range(f"B2:B{last_row}").value
        raw_prices = self.do_sheet.range(f"F2:F{last_row}").value

        self.price_list = []
        self.sku_list = []

        for sku, price in zip(raw_skus, raw_prices):
            if sku is None:
                continue

            cleaned_sku = sku.replace("Ü", "U")

            price = int(price) if isinstance(price, float) else 0

            if sku in ["FÜ80F", "FZN80"]:
                pass
            else:
                self.sku_list.append(cleaned_sku)
                self.price_list.append(price)

        do_dict = {
            "sku": self.sku_list,
            "price": self.price_list,
            "attribute": 7
        }
        do_data = pandas.DataFrame(do_dict)
        do_data.to_csv("Input/do.csv")
