FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y \
  git \
  wget \
  zip \
  curl \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*