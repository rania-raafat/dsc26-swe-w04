# AGENTS.md

## Project and source of truth
- This repository is the Nour Transfers testing task; use `SPEC.md` as the behavioural source of truth.
- Use Python 3.12 and the dependency versions pinned in `requirements.txt`.
- The transfer-card response contract is `contracts/transfer_card.schema.json`.
- Application code lives in `nour_transfers/`; tests belong under `tests/unit/`, `tests/api/`, or `tests/contract/`.

## Setup and verification
- Create the environment with `uv venv --python 3.12`.
- Install dependencies with `uv pip install -r requirements.txt`.
- In Git Bash, activate it with `source .venv/Scripts/activate`.
- Run the full suite from the repository root with `python -m pytest -q`.
- Run the focused task tests with `python -m pytest -q tests/unit tests/api tests/contract`.

## Test and API conventions
- Test only documented public functions and HTTP behaviour; do not import private helpers or inspect implementation internals.
- Exercise HTTP endpoints through FastAPI `TestClient`.
- Validate transfer-card responses against `contracts/transfer_card.schema.json`.
- API error responses use `application/problem+json`; assert the problem `type` as well as the HTTP status.
- Transfer-card JSON uses the documented camelCase field names, including `requestedAt`.
- `requestedAt` must retain its UTC `Z` timezone designator.
- Keep tests deterministic and offline; do not call external services.
- Do not use `skip`, `skipif`, or `xfail` to hide unmet requirements.

## Known trap and boundaries
- Different transfer conflicts can share HTTP 409; checking only the status can let the wrong error pass, so assert the documented problem type.
- This is a test-focused task: do not modify `nour_transfers/` or `contracts/` unless the task explicitly asks for implementation or contract changes.
- Keep each regression test focused on one documented behaviour and place it in the matching test directory.
- Before finishing, review `git diff` and report the actual test output; local passes do not prove hidden mutation tests pass.