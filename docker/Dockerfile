FROM python:3

WORKDIR /app
COPY . .
COPY ./docker/entrypoint.sh /entrypoint.sh

RUN apt-get update \
  && apt-get -y install graphviz \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r /app/requirements.txt

ENTRYPOINT ["/entrypoint.sh"]
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888"]
