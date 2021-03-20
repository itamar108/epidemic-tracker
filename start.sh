
# runs data server, waits 10s until its intialized, then runs our api.the kill0 enables us to kill everything in one ctrl+C


(trap 'kill 0' SIGINT; sleep 10 && python3 tracker_api.py & cd covid_server && cd dds && npm start)




