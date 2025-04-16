FROM python:3.9-slim

WORKDIR /app

# Install Werkzeug explicitly first
RUN pip install werkzeug==2.0.3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"] 