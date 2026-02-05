# 1. The Base Image: Start with a lightweight version of Python
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the dependencies file first (for caching speed)
COPY requirements.txt .

# 4. Install dependencies (Clean install)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your app code
# This copies your python scripts, the 'data' folder, and 'fed_db'
COPY . .

# 6. Expose the port Streamlit runs on
EXPOSE 8501

# 7. The Command to run the app
# We use the 'cloud' version (streamlit_app.py) because it's lightweight
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]