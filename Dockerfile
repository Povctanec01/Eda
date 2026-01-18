FROM python:3.13.2

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

RUN apt update && apt -qy install gcc libjpeg-dev libxslt-dev \
libpq-dev libmariadb-dev libmariadb-dev-compat gettext cron openssh-client flake8 locales vim

RUN useradd -rms /bin/basn eda && chmod 777 /opt /run

WORKDIR /eda

RUN mkdir /eda/static && mkdir /eda/media && chown -R eda:eda /eda && chmod 755 /eda

COPY --chown=eda:eda . .

RUN pip install -r requirements.txt

USER eda

CMD ["gunicoen","-b", "0.0.0.0:8001","soaqaz.wsgi:application"]