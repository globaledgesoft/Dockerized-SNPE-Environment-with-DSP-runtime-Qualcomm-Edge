# Start from Python 3.6 based on Debian Buster
FROM python:3.6-slim-buster

# Install vim and any additional utilities needed
RUN python3 -m pip install --upgrade pip
RUN apt-get update && \
    apt-get install -y vim libatomic1 libopencv-dev && \
    apt-get -y install gcc g++ mono-mcs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN python3 -m pip install --no-cache-dir decorator scipy psutil attrs tqdm typing-extensions opencv-python==4.5.3.56
RUN python3 -m pip install pybind11

# Create necessary directories
RUN mkdir -p /data/snpe-1.68.0.3932
RUN mkdir -p /usr/lib/rfsa/adsp
RUN mkdir -p /dsp

# Copy necessary files
COPY snpe-1.68.0.3932/include /data/snpe-1.68.0.3932/include/
COPY snpe-1.68.0.3932/lib/aarch64-ubuntu-gcc7.5/libSNPE.so /usr/lib/aarch64-linux-gnu/
COPY snpe-1.68.0.3932/lib/dsp/* /data/snpe-1.68.0.3932/
COPY snpe-1.68.0.3932/lib/aarch64-ubuntu-gcc7.5/* /data/snpe-1.68.0.3932/
COPY snpe-1.68.0.3932/bin/aarch64-ubuntu-gcc7.5/* /data/snpe-1.68.0.3932/
COPY build/rfsa/adsp /usr/lib/rfsa/adsp

# Copy the source to the appropriate directory
COPY src /data/snpe-1.68.0.3932/

# Compile qcsnpe.so
RUN g++ -std=c++11 -fPIC -shared -o /data/snpe-1.68.0.3932/qcsnpe.so /data/snpe-1.68.0.3932/qcsnpe.cpp \
    -I /data/snpe-1.68.0.3932/include/ \
    -I /data/snpe-1.68.0.3932/include/zdl/ \
    -I /usr/include/python3.6m/ \
    -I /usr/local/lib/python3.6/site-packages/pybind11/include/ \
    -I /usr/local/include/python3.6m/ \
    -L /data/snpe-1.68.0.3932/ \
    -lSNPE `pkg-config --cflags --libs opencv`

# Set environment variables
ENV PATH="/data/snpe-1.68.0.3932:$PATH"
ENV LD_LIBRARY_PATH="/data/snpe-1.68.0.3932:/usr/lib/rfsa/adsp:$LD_LIBRARY_PATH"
ENV ADSP_LIBRARY_PATH="/data/snpe-1.68.0.3932;/usr/lib/rfsa/adsp;/dsp"

# Default command 
CMD ["bin/bash"]

