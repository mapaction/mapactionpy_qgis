FROM  osgeo/gdal:ubuntu-full-3.4.1

# Install base utilities
RUN apt-get update 
RUN apt-get install -y software-properties-common ca-certificates wget curl ssh

RUN apt-get install -y build-essential && \
    apt-get install -y wget && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH

COPY environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

RUN conda run --no-capture-output -n myenv conda install -c anaconda pyqt
RUN conda run --no-capture-output -n myenv conda install -c conda-forge qgis
RUN conda run --no-capture-output -n myenv pip install Pillow
RUN conda run --no-capture-output -n myenv pip install python-resize-image
RUN conda run --no-capture-output -n myenv pip install psutil
RUN conda run --no-capture-output -n myenv pip install pdf2image
RUN git clone -b occamlabsqgis https://github.com/mapaction/mapactionpy_qgis.git 
RUN git clone -b occamlabsarcpro https://github.com/mapaction/mapactionpy_controller.git 
RUN conda run --no-capture-output -n myenv pip install -e mapactionpy_controller
RUN conda run --no-capture-output -n myenv pip install -e mapactionpy_qgis

COPY ./fonts/Eurostile.ttf ./
RUN install -m644 Eurostile.ttf /usr/share/fonts/truetype/
RUN rm ./Eurostile.ttf

ENV QGIS_PATH=/opt/conda/envs/myenv/share/qgis
ENV DISPLAY=host.docker.internal:0.0
