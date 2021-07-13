FROM tiangolo/uwsgi-nginx-flask:python3.7
ENV MONGO_HOST=mongo
ENV REDIS_HOST=redis
ADD start.sh /uwsgi-nginx-entrypoint.sh
ADD test
RUN chmod +x /uwsgi-nginx-entrypoint.sh
ADD requirement.txt /
ENV TIME_ZONE=Asia/Shanghai 
RUN ln -snf /usr/share/zoneinfo/$TIME_ZONE /etc/localtime && echo $TIME_ZONE > /etc/timezone
RUN pip install -r /requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
COPY . /app
