#!/bin/bash

# Synchronize trash annotations in the background
timeout 30 python /app/download.py

exec "$@"
