#!/bin/bash

# Simple Docker-only Health Database Backup Script
# This script creates a backup of the health.db file from any Docker container

set -e  # Exit on any error

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILENAME="health_backup_${TIMESTAMP}.db"
CONTAINER_DB_PATH="/app/data/health.db"
LOCAL_DB_PATH="./backups/health.db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Simple Docker Database Backup${NC}"
echo "=================================="

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Method 1: Check if file exists locally (volume mapping)
if [ -f "$LOCAL_DB_PATH" ]; then
    echo -e "${GREEN}✓ Found database in local volume${NC}"
    cp "$LOCAL_DB_PATH" "$BACKUP_DIR/$BACKUP_FILENAME"
    echo -e "${GREEN}✓ Backup created: $BACKUP_DIR/$BACKUP_FILENAME${NC}"
    exit 0
fi

# Method 2: Find and copy from running containers
echo "Searching for running containers with database..."

# Get all running container IDs
CONTAINERS=$(docker ps -q 2>/dev/null || echo "")

if [ -z "$CONTAINERS" ]; then
    echo -e "${RED}✗ No running containers found${NC}"
    echo ""
    echo "To start your container:"
    echo "  docker run -d -v \$(pwd)/data:/data [your-image-name]"
    exit 1
fi

# Check each container for the database file
for container_id in $CONTAINERS; do
    echo "Checking container: $container_id"

    # Check if the database file exists in this container
    if docker exec "$container_id" test -f "$CONTAINER_DB_PATH" 2>/dev/null; then
        echo -e "${GREEN}✓ Found database in container: $container_id${NC}"

        # Copy the file
        if docker cp "$container_id:$CONTAINER_DB_PATH" "$BACKUP_DIR/$BACKUP_FILENAME"; then
            echo -e "${GREEN}✓ Backup created: $BACKUP_DIR/$BACKUP_FILENAME${NC}"

            # Show file info
            if [ -f "$BACKUP_DIR/$BACKUP_FILENAME" ]; then
                FILE_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_FILENAME" | cut -f1)
                echo "  Size: $FILE_SIZE"
                echo "  Time: $(date)"
            fi
            exit 0
        else
            echo -e "${RED}✗ Failed to copy from container${NC}"
        fi
    fi
done

# If we get here, no database was found
echo -e "${RED}✗ Database file not found in any running container${NC}"
echo ""
echo "Troubleshooting:"
echo "1. Verify containers are running: docker ps"
echo "2. Check database path in container: docker exec [container-id] ls -la /data/"
echo "3. Ensure database file exists: docker exec [container-id] find / -name '*.db' 2>/dev/null"
exit 1
