# Update documentation for project structure and code standards

## Problem
Current documentation does not specify the repository rules:
- No code in the repository root.
- Source code must live in `Lyra-Project/src`.
- Tests must live in `Lyra-Project/src/tests`.
- `lyra.py` is the main entry point.
- All code must be fully type safe, memory safe, and well commented.

## Tasks
- [ ] Revise `README.md` to describe the required layout and entry point.
- [ ] Update `AGENTS.md` or other contributor docs with the code placement and quality rules.
- [ ] Ensure onboarding and contributor docs mention type safety, memory safety, and comment expectations.

## Acceptance Criteria
- Documentation clearly states where code and tests reside and that no code is stored in the root.
- `lyra.py` noted as the main entry point.
- Coding standards for type safety, memory safety, and comments are explicitly documented.
