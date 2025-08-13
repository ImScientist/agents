FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /main

# Install dependencies
RUN --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked

COPY src ./src

ENV PYTHONPATH=/main/src

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/app.py"]
