FROM base
RUN apt-get -y install software-properties-common python g++ make git
RUN apt-get update
RUN curl -kL http://xrl.us/pythonbrewinstall | bash
ADD . /src
RUN cd /src;
WORKDIR /src
EXPOSE 8080
ENTRYPOINT make -e PORT=8080 start
