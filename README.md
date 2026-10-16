# BTP Quote Manager

A small work-in-progress project for managing construction quotes (*devis BTP*). It is also a learning project to practice Python, FastAPI, TypeScript, and React.

## Current Status

The backend is implemented with Python and FastAPI. It currently validates quote items, calculates item and quote totals, and calculates VAT. A single API endpoint exposes quote-item total calculation.

The TypeScript and React frontend has not been started yet; they are learning goals for future development.

## Backend Features

- Immutable quote-item model with validation for descriptions, quantities, and unit prices.
- Exact decimal arithmetic for item and quote totals.
- VAT calculation with rates from 0 to 100 and rounding to two decimal places.
- FastAPI endpoint: `POST /quote-items/calculate`.
- Automated domain and API tests using pytest.

## Project Structure

```text
.
├── README.md
└── backend/
		├── app/
		│   ├── domain.py
		│   └── main.py
		├── tests/
		│   ├── test_api.py
		│   └── test_domain.py
		└── requirements.txt
```

## Requirements

- Python 3.10 or newer
- A terminal with `venv` support

## Set Up the Backend

Run these commands from the repository root.

### macOS and Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the API

With the virtual environment activated, from the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

The API is available at <http://127.0.0.1:8000>. FastAPI's interactive documentation is at <http://127.0.0.1:8000/docs>.

## API Example

Calculate the pre-tax total for a quote item:

```bash
curl -X POST http://127.0.0.1:8000/quote-items/calculate \
	-H "Content-Type: application/json" \
	-d '{"description":"Roof repair","quantity":"10","unit_price":"45.50"}'
```

Example response:

```json
{"total_ht":"455.00"}
```

## Run the Tests

From the `backend/` directory, with the virtual environment activated:

```bash
python -m pytest -v
```

## Learning Goals

- Grow the Python domain model and improve validation and financial-calculation tests.
- Build out the FastAPI backend and learn how to design and test HTTP APIs.
- Develop a TypeScript and React frontend that consumes the API.
- Connect the frontend and backend into a complete quote-management application.