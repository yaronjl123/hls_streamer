FROM python:3.9

WORKDIR /converter
RUN apt-get update && apt install -y ffmpeg
RUN pip3 install --upgrade pip
RUN pip3 install poetry
ADD converter/poetry.lock .
ADD converter/pyproject.toml .
RUN poetry install
ADD converter .
ADD common ./common
ADD config.yml ./config.yml

CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
