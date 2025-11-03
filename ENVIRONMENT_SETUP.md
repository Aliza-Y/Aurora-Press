# Environment Setup Guide

## Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here
GROQ_API_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_MODEL=mixtral-8x7b-32768

# Module 4 Visual Generation (Optional - for Colab integration)
COLAB_API_URL=https://your-ngrok-url.ngrok.io

# Module 7 Publishing & Distribution (Optional)
REDIS_URL=redis://localhost:6379/0
TWITTER_CLIENT_ID=your_twitter_client_id_here
TWITTER_CLIENT_SECRET=your_twitter_client_secret_here
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
LINKEDIN_CLIENT_ID=your_linkedin_client_id_here
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret_here
WORDPRESS_URL=your_wordpress_site_url_here
WORDPRESS_USERNAME=your_wordpress_username_here
WORDPRESS_APP_PASSWORD=your_wordpress_app_password_here
```

## How to Get API Keys

### 1. Groq API Key
1. Go to https://console.groq.com/
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it as `GROQ_API_KEY` in your `.env` file

### 2. MongoDB URI
1. Go to https://cloud.mongodb.com/
2. Sign up or log in
3. Create a new cluster (free tier available)
4. Go to Database Access and create a user
5. Go to Network Access and add your IP address
6. Go to Database and click "Connect"
7. Choose "Connect your application"
8. Copy the connection string and replace `<password>` with your actual password

## Current Issues

Based on the terminal output, you need to:

1. **Set up Groq API Key**: The 403 Forbidden error indicates the API key is missing or invalid
2. **Fix MongoDB Connection**: The timeout errors suggest network connectivity issues

## Quick Fix Commands

```bash
# Create .env file
touch .env

# Add your environment variables
echo "GROQ_API_KEY=your_actual_key_here" >> .env
echo "MONGO_URI=your_mongodb_connection_string_here" >> .env

# Restart the backend
pkill -f "uvicorn main:app"
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
