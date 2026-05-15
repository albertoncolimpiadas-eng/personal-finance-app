from pathlib import Path

from sqlalchemy.engine import Engine


def test_tests_use_temporary_sqlite_database(test_engine: Engine) -> None:
    database_path = Path(test_engine.url.database or "")

    assert database_path.name == "finance-test.db"
    assert database_path.exists()
    assert Path("data/finance.db").resolve() != database_path.resolve()
