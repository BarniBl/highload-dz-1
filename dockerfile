FROM python:3.7.2-alpine3.8
LABEL maintainer="BarniBl"
RUN apk update && apk upgrade && apk add bash
COPY . .
EXPOSE 8000
CMD ["python3", "./server.py"]