"""Run once per hour on the server to process paid-team subscription renewals."""

import logging

from Backend.database import SessionLocal
from Backend.main import process_due_renewals


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    db = SessionLocal()
    try:
        result = process_due_renewals(db)
        logging.info("Subscription renewal result: %s", result)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
