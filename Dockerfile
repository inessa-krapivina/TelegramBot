FROM fnndsc/python-poetry

COPY pyproject.toml /
COPY poetry.lock /

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-root

COPY ./ /

CMD ["poetry", "run", "python3", "main.py"]
