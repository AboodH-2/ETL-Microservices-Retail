FROM python:3.9-slim

WORKDIR /app

# Install dependencies in the correct order
RUN pip install werkzeug==2.0.3
RUN pip install numpy==1.20.3
RUN pip install pandas==1.3.3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "app.py"] 