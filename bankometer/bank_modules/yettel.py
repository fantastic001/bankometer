
import time
from bs4 import BeautifulSoup
import pandas as pd 
import datetime
import pdfplumber

import re

from bankometer.bank_modules import StatementProcessor 
from pathlib import Path

class YettelStatementProcessor(StatementProcessor):

    def _parse_amount(self, x: str) -> float:
        return float(x.replace(".", "").replace(",", "."))
    
    def _parse_table(self, page_text: str) -> list[list[str | float]]:
        rows = []
        lines = page_text.split("\n")

        pattern = re.compile(
            r"^\d+\s+(.*?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{2}\.\d{2}\.\d{4})\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)"
        )

        for line in lines:
            m = pattern.search(line)
            if m:
                opis, d1, d2, isplata, uplata, stanje = m.groups()
                rows.append([
                    opis.strip(),
                    d1,
                    d2,
                    self._parse_amount(isplata),
                    self._parse_amount(uplata),
                    self._parse_amount(stanje),
                ])
        return rows

    def process_statement(self, statement_path: Path) -> dict[str, float | int | str]:
        usd_rows = []
        rsd_rows = []
        eur_rows = []
        with pdfplumber.open(statement_path) as pdf:
            current = None
            for page in pdf.pages:
                text = page.extract_text()

                if "Izvod po valuti: USD" in text:
                    current = "USD"
                elif "Izvod po valuti: RSD" in text:
                    current = "RSD"
                elif "Izvod po valuti: EUR" in text:
                    current = "EUR"

                rows = self._parse_table(text)

                if current == "USD":
                    usd_rows.extend(rows)
                elif current == "RSD":
                    rsd_rows.extend(rows)
                elif current == "EUR":
                    eur_rows.extend(rows)
        usd_df = pd.DataFrame(usd_rows, columns=[
            "opis", "datum_knjizenja", "datum_valute",
            "isplata", "uplata", "stanje"
        ])
        rsd_df = pd.DataFrame(rsd_rows, columns=[
            "opis", "datum_knjizenja", "datum_valute",
            "isplata", "uplata", "stanje"
        ])
        eur_df = pd.DataFrame(eur_rows, columns=[
            "opis", "datum_knjizenja", "datum_valute",
            "isplata", "uplata", "stanje"
        ])

        rsd_df = rsd_df.rename(columns={
            "isplata": "credit",
            "uplata": "debit",
            "stanje": "balance",
            "datum_knjizenja": "accounting_date",
            "datum_valute": "date",
            "opis": "description",
        })
        usd_df = usd_df.rename(columns={
            "isplata": "credit",
            "uplata": "debit",
            "stanje": "balance",
            "datum_knjizenja": "accounting_date",
            "datum_valute": "date",
            "opis": "description",
        })
        eur_df = eur_df.rename(columns={
            "isplata": "credit",
            "uplata": "debit",
            "stanje": "balance",
            "datum_knjizenja": "accounting_date",
            "datum_valute": "date",
            "opis": "description",
        })
        current_time = datetime.datetime.now().timestamp()
        usd_csv_name = f"yettel_usd_{current_time}.csv"
        rsd_csv_name = f"yettel_rsd_{current_time}.csv"
        eur_csv_name = f"yettel_eur_{current_time}.csv"
        usd_df.to_csv(usd_csv_name, index=False)
        rsd_df.to_csv(rsd_csv_name, index=False)
        eur_df.to_csv(eur_csv_name, index=False)
        return {
            "USD": usd_csv_name,
            "RSD": rsd_csv_name,
            "EUR": eur_csv_name,
            "USD_total_spent": usd_df["credit"].sum(),
            "RSD_total_spent": rsd_df["credit"].sum(),
            "EUR_total_spent": eur_df["credit"].sum(),
            "USD_total_received": usd_df["debit"].sum(),
            "RSD_total_received": rsd_df["debit"].sum(),
            "EUR_total_received": eur_df["debit"].sum(),
        }


        

if __name__ == "__main__":
    interface = Yettel({})
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=1)
    interface.login()
    data = interface.get_transactions(start_date, today)
    print(data)