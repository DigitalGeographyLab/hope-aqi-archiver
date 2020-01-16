FROM continuumio/miniconda3

ADD src /app/src
WORKDIR /app/src
RUN conda env create -f env_aqi_archiver.yml && conda clean -afy
ENV PATH /opt/conda/envs/aqi-archiver/bin:$PATH

CMD python aqi_archiver_app.py
