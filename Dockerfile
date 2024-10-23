FROM tiangolo/uvicorn-gunicorn:python3.10 AS bitvmx-base

RUN apt-get update

RUN apt-get install -y \
    build-essential \
    curl

RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

RUN pip install --upgrade pip

COPY requirements/base.txt /tmp/requirements/

RUN pip install -r /tmp/requirements/base.txt

## We need to install it manually due to the existent bug

#RUN pip install --no-cache-dir git+https://github.com/karask/python-bitcoin-utils.git@0c99998136e21f4ec055f2842bdf674aae611c18
#RUN pip install --no-cache-dir git+https://github.com/ramonamela/python-bitcoin-utils.git@5392fec4f6b149cf7d913d65640b619727e976ef
RUN pip install --no-cache-dir git+https://github.com/ramonamela/python-bitcoin-utils.git@3e8c2a0bf1b080ed5f80f4e78f71005f42eb52c5
#RUN pip install --no-cache-dir git+https://github.com/ramonamela/python-bitcoin-utils.git@5b213cb10a6fe810fb9c0606608bfbc05789cd3a

RUN pip install --no-cache-dir git+https://github.com/ramonamela/pybitvmbinding.git@2cb13f79fca1e0da47305a102eeb66fc5982a9e1

RUN mkdir /bitvmx-backend

WORKDIR /bitvmx-backend

COPY ./BitVMX-CPU ./BitVMX-CPU
COPY ./blockchain_query_services ./blockchain_query_services

WORKDIR /bitvmx-backend/BitVMX-CPU

RUN cargo build

WORKDIR /bitvmx-backend

FROM bitvmx-base as prover-backend

RUN pip install --upgrade pip

COPY requirements/prover.txt /tmp/requirements/

RUN pip install -r /tmp/requirements/prover.txt

COPY ./prover_app ./prover_app
RUN mkdir prover_files

CMD ["uvicorn", "prover_app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug", "--lifespan", "on"]

FROM bitvmx-base as verifier-backend

RUN pip install --upgrade pip

COPY requirements/verifier.txt /tmp/requirements/

RUN pip install -r /tmp/requirements/verifier.txt

COPY ./verifier_app ./verifier_app
RUN mkdir verifier_files

CMD ["uvicorn", "verifier_app.main:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug", "--lifespan", "on"]