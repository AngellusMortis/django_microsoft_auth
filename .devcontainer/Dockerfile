FROM python:3.11-slim-buster as base

LABEL org.opencontainers.image.source https://github.com/AngellusMortis/django_microsoft_auth

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


FROM base as builder

RUN --mount=type=cache,mode=0755,id=apt,target=/var/lib/apt/lists apt-get update -qq \
    && apt-get install -yqq build-essential

COPY ./reqs/dj4.1-requirements.txt /
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install -U pip \
    && pip install -r /dj4.1-requirements.txt \
    && rm /dj4.1-requirements.txt


FROM base as dev

COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /usr/local/lib/python3.11/ /usr/local/lib/python3.11/
RUN --mount=type=cache,mode=0755,id=apt,target=/var/lib/apt/lists apt-get update \
    && apt-get install -y git vim curl \
    && echo 'export PS1="\[$(tput setaf 6)\]\w \[$(tput setaf 7)\]\\$ \[$(tput sgr0)\]"' >> /root/.bashrc

ENV PATH /workspaces/django_microsoft_auth/.bin:$PATH
ENV PYTHONPATH /workspaces/django_microsoft_auth/
