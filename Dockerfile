FROM tiangolo/uvicorn-gunicorn:python3.10 AS bitvmx-base

RUN pip install --upgrade pip

COPY requirements/base.txt /tmp/requirements/

RUN pip install -r /tmp/requirements/base.txt

RUN mkdir /bitvmx-backend

WORKDIR /bitvmx-backend

COPY . ./

FROM bitvmx-base as prover-backend

RUN pip install --upgrade pip

COPY requirements/prover.txt /tmp/requirements/

RUN pip install -r /tmp/requirements/prover.txt

COPY . ./

CMD ["uvicorn", "prover_app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug", "--lifespan", "on"]

FROM bitvmx-base as verifier-backend

RUN pip install --upgrade pip

COPY requirements/verifier.txt /tmp/requirements/

RUN pip install -r /tmp/requirements/verifier.txt

COPY . ./

CMD ["uvicorn", "verifier_app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug", "--lifespan", "on"]