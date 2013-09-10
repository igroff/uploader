FROM uploader_base:latest
RUN useradd uploader -m -d /home/uploader -s /bin/bash
RUN passwd -d uploader
RUN su uploader -c "curl -kL http://xrl.us/pythonbrewinstall | bash"
RUN su uploader -c "source ~/.pythonbrew/etc/bashrc && pythonbrew install 2.7.2 && pythonbrew switch 2.7.2"
ADD . /home/uploader
WORKDIR /home/uploader
RUN chown -R uploader:uploader /home/uploader
RUN su uploader -c "/bin/bash -ic 'make build'"
EXPOSE 8080
ENTRYPOINT su uploader -c "/bin/bash -ic 'make -e PORT=8080 start'"
