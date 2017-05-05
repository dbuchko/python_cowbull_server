FROM		python:3.5.3-slim
MAINTAINER	David Sanders
RUN			apt-get update && \
			groupadd -r cowbull_g && \
			mkdir /cowbull && \
			useradd -r -G cowbull_g -d /cowbull cowbull && \
			chown cowbull /cowbull
WORKDIR		/cowbull
COPY		requirements.txt /cowbull
RUN		    pip install -q -r /cowbull/requirements.txt
USER		cowbull
#VOLUME		/cowbull/src
ENV			PYTHONPATH="/cowbull"
#ENV         redis_host="redis"
COPY		python_cowbull_server /cowbull/python_cowbull_server/
COPY        flask_controllers /cowbull/flask_controllers/
COPY        flask_helpers /cowbull/flask_helpers
COPY        Persistence /cowbull/Persistence/
COPY        app.py  /cowbull/
COPY        LICENSE /cowbull/
CMD			["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "app:app"]
EXPOSE		5000