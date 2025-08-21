FROM python:3.11.2-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY ./Requirements.txt /app/Requirements.txt

RUN pip install -r Requirements.txt

COPY ./scheduling /app/scheduling
COPY ./execute_scheduling.py /app/execute_scheduling.py
COPY ./set_general_scheduling_parameters.py /app/set_general_scheduling_parameters.py
COPY ./run_services.py /app/run_services.py

CMD ["python", "/app/run_services.py"]

EXPOSE 5000
