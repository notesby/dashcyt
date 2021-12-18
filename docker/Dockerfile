FROM continuumio/anaconda3 as builder

RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update
RUN apt-get install -y gnupg2 wget make zlib1g-dev build-essential libssl-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN apt-get install -y unixodbc-dev

RUN apt-get install -y git
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"
ENV PYTHON_VERSION=3.8.2
RUN git clone https://github.com/pyenv/pyenv-virtualenv.git $(PYENV_ROOT)/plugins/pyenv-virtualenv
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
RUN /bin/bash -l
RUN pyenv install ${PYTHON_VERSION}
RUN pyenv global ${PYTHON_VERSION}

FROM builder as build1

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH ${PATH}:/root/.poetry/bin

FROM build1 as build2
COPY . /dashcyt
WORKDIR /dashcyt
RUN pyenv local ${PYTHON_VERSION}
RUN poetry config virtualenvs.in-project true
RUN poetry install

FROM build2 as build3
ENV FLASK_APP="dashcyt/wsgi.py"
ENV FLASK_ENV=development

#RUN conda env create -f dashboard.yml
#RUN echo "conda activate dashboard" > ~/.bashrc
#ENV PATH /opt/conda/envs/dashboard/bin:$PATH

