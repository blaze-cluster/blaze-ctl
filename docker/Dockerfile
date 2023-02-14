FROM python:3.10-buster

RUN apt update && \
      curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.24.7/2022-10-31/bin/linux/amd64/kubectl && \
      chmod +x ./kubectl && \
      mv ./kubectl /bin/

RUN pip install blazectl==0.5.0

WORKDIR /root
ADD config/* .blazectl/
ADD scripts/* ./
RUN chmod +x *.sh

SHELL ["/bin/bash", "-c"]

ENTRYPOINT [ "blazectl" ]
CMD [ "--help" ]