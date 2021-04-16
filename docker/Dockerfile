FROM python:3.8

RUN apt-get update -qq \
  && apt-get -y install graphviz python3-opencv \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./docker/requirements.txt /app/docker/requirements.txt

RUN pip3 install --upgrade --no-cache-dir --no-binary \
    Cython==0.29.21 \
    numpy==1.19.2 \
  && pip3 install -r /app/docker/requirements.txt

COPY . .

COPY ./docker/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888"]
