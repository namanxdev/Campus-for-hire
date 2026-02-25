#!/bin/bash
set -e

echo "========================================"
echo "  Campus-to-Hire API Startup Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Wait for database to be ready
wait_for_db() {
    log_info "Waiting for database connection..."
    
    local max_retries=30
    local retry_count=0
    
    while [ $retry_count -lt $max_retries ]; do
        if python -c "
import sys
from sqlalchemy import create_engine
from app.config import settings

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        print('Database connection successful')
        sys.exit(0)
except Exception as e:
    print(f'Connection failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
            log_info "Database is ready!"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        log_warn "Database not ready yet. Attempt $retry_count/$max_retries. Retrying in 2 seconds..."
        sleep 2
    done
    
    log_error "Failed to connect to database after $max_retries attempts"
    return 1
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    if alembic upgrade head; then
        log_info "Migrations completed successfully!"
    else
        log_error "Failed to run migrations"
        return 1
    fi
}

# Create logs directory if it doesn't exist
setup_logs() {
    mkdir -p /app/logs
    log_info "Logs directory ready"
}

# Main startup sequence
main() {
    log_info "Starting Campus-to-Hire API..."
    
    # Setup logs
    setup_logs
    
    # Wait for database
    if ! wait_for_db; then
        log_error "Database connection failed. Exiting..."
        exit 1
    fi
    
    # Run migrations
    if ! run_migrations; then
        log_error "Migration failed. Exiting..."
        exit 1
    fi
    
    # Determine worker count based on available CPUs
    WORKERS=${UVICORN_WORKERS:-4}
    log_info "Starting Uvicorn with $WORKERS workers..."
    
    # Start the application with uvicorn
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port ${PORT:-8000} \
        --workers $WORKERS \
        --loop uvloop \
        --http httptools \
        --proxy-headers \
        --forwarded-allow-ips '*' \
        --access-log \
        --error-log \
        --log-level info
}

# Run main function
main "$@"
