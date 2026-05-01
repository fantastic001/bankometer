
from bankometer.bank_modules import StatementProcessor
from bankometer.bank_modules.yettel import YettelStatementProcessor


def get_statement_processor(bank_name: str) -> StatementProcessor:
    try:
        return {
            "yettel": YettelStatementProcessor(),
        }[bank_name]
    except KeyError:
        raise ValueError(f"Unsupported bank: {bank_name}")