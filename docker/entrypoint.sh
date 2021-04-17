#!/bin/bash

# Synchronize trash annotations in the background
timeout 30 /app/download.py

exec "$@"
