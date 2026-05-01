
from abc import abstractmethod
from pathlib import Path

class StatementProcessor:
    @abstractmethod
    def process_statement(self, statement_path: Path) -> dict[str, float | int | str]:
        pass