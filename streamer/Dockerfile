FROM python:3.9

WORKDIR /streamer
RUN pip3 install --upgrade pip
RUN pip3 install poetry
ADD streamer/poetry.lock .
ADD streamer/pyproject.toml .
RUN poetry install
ADD streamer .
ADD common ./common
ADD config.yml ./config.yml

CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]