
FROM node:15-buster-slim
WORKDIR /app
COPY . /app
RUN cd ./covid_server && cd dds && npm install

#when trying greater than python3, still didn't work.
RUN apt-get update || : && apt-get install python3 -y
RUN apt-get install python3-pip -y
RUN pip3 install -r ./requirements.txt


EXPOSE 5001

CMD ./start.sh


# run command
# docker run --name app_image -p 5001:5001 app_image
