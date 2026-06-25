# Base image with python 3.14.4
FROM python:3.14.4-bookworm 

# Set a working directory inside the container
WORKDIR /backend

# Installing requirements (uv) for the container
# --no-cache-dir prevents pip cache buildup
RUN pip install --no-cache-dir uv

# Copying of dependencies separated from source code to improve efficiency
# Docker does layer caching, so if dependencies are unchanged, docker won't run this again
COPY pyproject.toml uv.lock ./

# Install dependencies, if above is unchanged, this don't run
RUN uv sync

# Copying source file; If source code changes, Docker rebuilds from this point onwards
COPY . .

# Expects traffic on port 8000
EXPOSE 8000

# Sets fixed executor prompt
ENTRYPOINT ["uv", "run", "uvicorn"]

# Running commands will always have ENTRYPOINT
# --app-dir looks for app inside src
# --host: binds server to all interfaces; Without this the container becomes unaccessible from host
CMD ["--app-dir", "src", "--host", "0.0.0.0", "app:app"] 