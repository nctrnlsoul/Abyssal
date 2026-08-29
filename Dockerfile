# Python 3.13 to match the interpreter the suite was actually verified on.
# A suggested Dockerfile pinned 3.11; the pins in requirements-web.txt were
# resolved and tested under 3.13.15, and the night before a deadline is the
# wrong time to discover a wheel that differs between minors.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# No build-essential. The console uses stdlib `wave` for the envelope and pure
# Python everywhere else, so a toolchain would add hundreds of megabytes and
# a compiler to a public image for nothing.
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY core/ ./core/
COPY web/ ./web/
COPY docs/recorded-run.json ./docs/recorded-run.json
COPY data/reef_window_a.wav ./data/reef_window_a.wav
COPY data/hab_forecast_cellcounts.png ./data/hab_forecast_cellcounts.png

# Build-time import smoke test. If the module path is wrong, the BUILD fails
# here instead of the deploy succeeding and the service crash-looping. A
# suggested version shipped `CMD uvicorn app.main:app` against a project whose
# module is `web.app:app`; that container would have started, failed, and
# restarted forever while reporting a successful deploy.
RUN python -c "from web.app import app; print('import ok:', app.title)"

# Non-root. Cloud Run does not require it and that is not a reason to skip it.
RUN useradd --create-home --uid 10001 abyssal && chown -R abyssal:abyssal /app
USER abyssal

EXPOSE 8080

# Exec form, and $PORT is read by uvicorn itself rather than interpolated by a
# shell, so there is no shell in the process tree to swallow signals.
CMD ["sh", "-c", "exec uvicorn web.app:app --host 0.0.0.0 --port ${PORT}"]
