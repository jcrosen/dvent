ARG DVENT_PYTHON_VERSION=3.6.5
FROM python:${DVENT_PYTHON_VERSION} as dvent
RUN groupadd -r dvent -g 1000 &&\
    useradd --no-log-init -r -g dvent -u 1000 dvent &&\
    mkdir -p /project/run &&\
    chown -R dvent:dvent /project/run
WORKDIR /project/run
COPY --chown=dvent:dvent ./dvent /project/run/dvent
COPY --chown=dvent:dvent ./setup.py /project/run/setup.py
COPY --chown=dvent:dvent ./README.rst /project/run/README.rst
RUN pip install -e .
USER dvent
CMD ["python", "-i"]

FROM dvent as dvent-test
USER root
RUN pip install "behave>=1.2.6,<2"
USER dvent
COPY --chown=dvent:dvent ./features /project/run/features
CMD ["behave"]

FROM dvent-test as dvent-jupyter
USER root
RUN mkdir -p /home/dvent &&\
    chown -R dvent:dvent /home/dvent
RUN pip install "jupyter>=1.0.0,<2"
USER dvent
COPY --chown=dvent:dvent ./notebooks /project/run/notebooks
ENTRYPOINT ["jupyter"]
CMD ["console"]
