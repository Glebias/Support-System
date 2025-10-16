.PHONY: run

run:
	uvicorn backend.main:app --reload
