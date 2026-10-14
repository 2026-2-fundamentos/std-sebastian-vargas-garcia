import csv
import json
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parents[1]
INPUT_FILE = PROJECT_FOLDER / "data" / "drivers.csv"
OUTPUT_FILE = PROJECT_FOLDER / "submission" / "drivers.json"

REQUIRED_COLUMNS = ("driverId", "name", "certified", "wage-plan")
SENSITIVE_COLUMNS = ("ssn", "location")


def read_csv_records(input_file):
    """Read a CSV file and return its headers and records."""
    input_file = Path(input_file)

    with input_file.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        headers = reader.fieldnames

        if headers is None:
            raise ValueError("El archivo CSV debe incluir encabezados.")
        if len(headers) != len(set(headers)):
            raise ValueError("Los encabezados del CSV no pueden repetirse.")

        records = list(reader)

    return headers, records


def validate_required_columns(headers):
    """Verify that the analytical export can identify each driver."""
    missing_columns = sorted(set(REQUIRED_COLUMNS) - set(headers))

    if missing_columns:
        missing_columns = ", ".join(missing_columns)
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}.")


def make_safe_records(records):
    """Keep only the fields needed for the analytical driver export."""
    return [
        {
            column: value
            for column, value in record.items()
            if column not in SENSITIVE_COLUMNS
        }
        for record in records
    ]


def write_json_records(records, output_file):
    """Write records as UTF-8 JSON, creating the destination folder if necessary."""
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)


def convert_csv_to_json(input_file, output_file):
    """Validate, minimize and serialize driver data from CSV to JSON."""
    headers, records = read_csv_records(input_file)
    validate_required_columns(headers)
    safe_records = make_safe_records(records)
    write_json_records(safe_records, output_file)
    return safe_records


def main():
    """Create the classroom JSON export in the submission folder."""
    convert_csv_to_json(INPUT_FILE, OUTPUT_FILE)


if __name__ == "__main__":
    main()
