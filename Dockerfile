FROM ubuntu:20.04
#FROM ubuntu:18.04
#FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip
RUN apt-get install -y xvfb x11-xkb-utils
RUN apt-get install -y xfonts-100dpi xfonts-75dpi xfonts-scalable xfonts-cyrillic
#RUN apt-get install -y python3-matplotlib python3-vtk

RUN apt-get install -y python3-pandas

RUN pip3 install vtk numpy cython scipy h5py nibabel nipype
RUN pip3 install cvxpy scikit-learn
RUN pip3 install dipy fury joblib nibabel

RUN pip3 install xvfbwrapper

#make it work under singularity
#RUN ldconfig && mkdir -p /N/u /N/home /N/dc2 /N/soft

#prevent ~/.local from getting loaded (doesn't look like it's working..?)
ENV PYTHONNOUSERSITE=true
ENV PYTHONIOENCODING=utf8

#https://wiki.ubuntu.com/DashAsBinSh
RUN rm /bin/sh && ln -s /bin/bash /bin/sh
