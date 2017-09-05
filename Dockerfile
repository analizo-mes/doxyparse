FROM debian:stretch

RUN useradd -ms /bin/bash analizo

# Set the working directory to /app
WORKDIR /home/doxyparse

# Copy the current directory contents into the container at /home/analizo
# ADD . /home/doxyparse

# Install any needed packages specified in requirements.txt
RUN apt-get -y update && apt-get -y install sudo apt-utils && apt-get -y clean
RUN apt-get install -y wget gnupg cmake make build-essential python c++11 flex bison git

# adding Permission to user
RUN chown -R analizo:analizo /home/doxyparse

# RUN mkdir -p /home/doxyparse/build && \
# cd /home/doxyparse/build && \
# cmake -G "Unix Makefiles" /home/doxyparse/

# Install Analizo/metrics
RUN git clone -b stable https://github.com/analizo-mes/analizo.git /home/stable
RUN ["chmod", "+x", "/home/stable/development-setup.sh"]
RUN cd /home/stable/ && ./development-setup.sh

# Execute tests
CMD mkdir -p /home/doxyparse/build && \
cd /home/doxyparse/build && \
cmake -G "Unix Makefiles" /home/doxyparse/ && \
make -j4 && \
make install && \
cd /home/stable/ && perl -I. test.pl
