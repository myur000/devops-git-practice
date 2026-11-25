FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Barnaul
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash tar gzip coreutils findutils util-linux cron python3 php-cli curl shellcheck tzdata \
    && rm -rf /var/lib/apt/lists/*
RUN ln -snf /usr/share/zoneinfo/Asia/Barnaul /etc/localtime \
    && printf 'Asia/Barnaul\n' > /etc/timezone
WORKDIR /work
CMD ["/bin/bash"]
