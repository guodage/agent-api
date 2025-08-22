FROM python:3.12-slim-bookworm

ARG USER=app
ARG APP_DIR=/app
ENV APP_DIR=${APP_DIR}

# Create user and home directory
RUN groupadd -g 61000 ${USER} \
  && useradd -g 61000 -u 61000 -ms /bin/bash -d ${APP_DIR} ${USER}

WORKDIR ${APP_DIR}

# Copy requirements.txt
COPY requirements.txt ./

# Install requirements in smaller batches with mirrors
RUN pip install --no-cache-dir --timeout=600 --retries=5 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    -r requirements.txt

# Copy project files
COPY . .

# Set permissions for the /app directory
RUN chown -R ${USER}:${USER} ${APP_DIR}

# Switch to non-root user
USER ${USER}

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["chill"]
