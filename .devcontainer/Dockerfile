FROM python:3.9-slim-buster    

WORKDIR /app                   

COPY requirements.txt .       

RUN pip install --no-cache-dir -r requirements.txt  

COPY bot.py .                 

# CMD ["python", "bot.py"]      