FROM python:3.6-jessie

# Copy the base uWSGI ini file to enable default dynamic uwsgi process number
COPY /summarizer_service /summarizer_service

# Add app
WORKDIR /summarizer_service

# Make /app/* available to be imported by Python globally
ENV PYTHONPATH=/summarizer_service

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "run.py"]