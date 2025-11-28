#!/bin/bash
set -e

echo "Installing backend dependencies..."
pip install -r requirements.txt

echo "Installing Node.js and building frontend..."
cd ../frontend

# Create .env file for build if environment variables are set
if [ -n "$VITE_SUPABASE_URL" ]; then
  echo "VITE_SUPABASE_URL=$VITE_SUPABASE_URL" > .env
  echo "VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY" >> .env
  echo "VITE_API_URL=$VITE_API_URL" >> .env
fi

npm ci
npm run build

echo "Build complete!"
