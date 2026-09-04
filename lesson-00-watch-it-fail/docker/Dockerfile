FROM python:3.12-slim
WORKDIR /lesson
COPY . .
RUN python3 -m venv /lesson/.venv --system-site-packages
CMD ["/lesson/.venv/bin/python3", "demo_agent.py", "demo", "--instance", "a", "--fixture"]
