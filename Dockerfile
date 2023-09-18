FROM zetabankhub/edu:melodic-pm2
ARG DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]
RUN apt-get update \
    && apt-get install -y apt-utils
RUN apt-get update \
    && apt-get install -y python-pip \
    && python -m pip install --upgrade pip \
    && apt-get install -y python-pyqt5 python3-pyqt5 pyqt5-dev-tools qttools5-dev-tools python-pyqt5.qtsql python3-pyqt5.qtsql python-pyqt5.qtmultimedia python3-pyqt5.qtmultimedia libqt5multimedia5-plugins
RUN apt-get install -y fonts-unfonts-core python-pygame python-requests

RUN echo "source ~/ws/install/setup.bash" >> ~/.bashrc
COPY billboard /root/billboard
CMD source /opt/ros/$ROS_DISTRO/setup.sh && /bin/bash

# docker build -t zetabankhub/edu:melodic-billboard-v0.0.1 -f Dockerfile .
