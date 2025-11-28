#!/bin/bash
set -e

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Installing Node.js and building frontend..."
cd ../frontend
npm ci
npm run build

echo "Build complete!"
