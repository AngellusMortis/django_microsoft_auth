FROM python:3.10-slim-buster

RUN apt-get update \
    && apt-get install -y git build-essential vim curl \
    # cleaning up unused files
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

COPY ./reqs/dev-requirements.txt /dev-requirements.txt
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -r /dev-requirements.txt \
    && rm /dev-requirements.txt \
    && echo 'export PS1="\[$(tput setaf 6)\]\w \[$(tput setaf 7)\]\\$ \[$(tput sgr0)\]"' >> /root/.bashrc

ENV PATH /workspaces/django_microsoft_auth/.bin:$PATH
ENV PYTHONPATH /workspaces/django_microsoft_auth/
ENV FLIT_ROOT_INSTALL=1
