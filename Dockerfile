FROM minizinc/minizinc:2.5.5

LABEL org.opencontainers.image.source=https://github.com/TechlauncherFireApp/backend
LABEL org.opencontainers.image.description="A web API designed to efficiently manage and schedule volunteer firefighters."
LABEL org.opencontainers.image.licenses=MIT

# Install Python3.8 and some packages
RUN apt update \
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -yqq pkg-config wget git gnupg curl python3.8 python3-pip libmysqlclient-dev
RUN pip3 install pipenv
RUN pip3 install gunicorn

# Copy source files
COPY . /app
WORKDIR /app
RUN pipenv install --system --deploy --ignore-pipfile

# Expose web server port & execute
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers=2", "--threads=2", "--timeout=1800", "--log-level=debug", "--pythonpath", "/", "application:app"]