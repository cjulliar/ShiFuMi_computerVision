FROM python:3.10

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  && apt-get install -y \
  git \
  wget \
  zip \
  curl \
  libgl1-mesa-glx \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*