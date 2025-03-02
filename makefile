init:
	python3 -m venv .venv
	echo "set environment config by running: source .venv/bin/activate"

install:
	pip install -r requirements.txt

run:
	streamlit run Author_Tool.py
