# --- Build Stage ---
# Use a specific, slim version of Python for a smaller base image.
FROM python:3.12-slim as builder

# Set environment variables for a clean and efficient build.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Install system dependencies required for building Python packages.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry, a modern dependency management tool.
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to the system's PATH.
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set the working directory.
WORKDIR /app

# Copy only the files necessary for installing dependencies.
# This leverages Docker's layer caching.
COPY poetry.lock pyproject.toml ./

# Install dependencies using Poetry.
# --only main installs only production dependencies.
RUN poetry install --no-root --only main


# --- Final Stage ---
# Use a clean, minimal base image for the final application.
FROM python:3.12-slim as final

# Set environment variables for the runtime.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_APP="app:create_app()" \
    FLASK_ENV="production" \
    GUNICORN_CONF="/app/deployment/gunicorn.conf.py"

# Install only runtime system dependencies.
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user for running the application.
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set the working directory.
WORKDIR /app

# Copy the virtual environment from the builder stage.
COPY --from=builder /app/.venv .venv

# Copy the application code.
COPY . .

# Create and set permissions for necessary directories.
RUN mkdir -p instance logs uploads && \
    chown -R appuser:appgroup /app

# Switch to the non-root user.
USER appuser

# Expose the port the app runs on.
EXPOSE 5000

# Healthcheck to ensure the application is running correctly.
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD [ "curl", "-f", "http://localhost:5000/api/status" ]

# Set the entrypoint to activate the virtual environment.
ENTRYPOINT [ "/app/.venv/bin/gunicorn", "--config", "deployment/gunicorn.conf.py", "app:create_app()" ]
