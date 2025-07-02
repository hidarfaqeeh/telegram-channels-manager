# Dockerfile for Telegram Channels Manager Bot
# Multi-stage build for optimized image size

FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    WORKDIR="/app"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    ffmpeg \
    imagemagick \
    libmagic1 \
    sqlite3 \
    tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Create non-root user for security
RUN groupadd -r botuser && useradd -r -g botuser botuser

# Create application directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /app/data \
    /app/logs \
    /app/sessions \
    /app/media/downloads \
    /app/media/uploads \
    /app/media/temp \
    && chown -R botuser:botuser /app

# Copy application files
COPY --chown=botuser:botuser . .

# Create .env file from example if it doesn't exist
RUN if [ ! -f .env ]; then cp .env.example .env; fi

# Set proper permissions
RUN chmod +x run.sh && \
    chmod +x setup_bot.py && \
    find . -name "*.py" -exec chmod 644 {} \;

# Health check script
COPY --chown=botuser:botuser <<EOF /app/healthcheck.py
#!/usr/bin/env python3
import sys
import os
import asyncio
import aiohttp

async def health_check():
    try:
        # Check if main modules can be imported
        sys.path.insert(0, '/app')
        import config
        from database.database import DatabaseManager
        
        # Check database connection
        db = DatabaseManager()
        await db.init_database()
        
        print("✅ Health check passed")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(health_check())
    sys.exit(0 if result else 1)
EOF

RUN chmod +x /app/healthcheck.py

# Switch to non-root user
USER botuser

# Expose port for potential web interface
EXPOSE 8080

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 /app/healthcheck.py

# Default command
CMD ["python3", "main.py"]