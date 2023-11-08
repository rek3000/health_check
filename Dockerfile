# FROM archlinux:base
# FROM python:3.11-slim
# FROM alpine:3.18
# FROM frolvlad/alpine-glibc
# RUN ln -s /lib/libcrypto.so /lib/libcrypto.so.3
# RUN apt update -y
# RUN apt install --no-install-recommends fonts-dejavu-core libmagickwand-dev -y
# RUN apt clean && rm -rf /var/lib/apt/lists/*
# RUN --mount=type=cache,sharing=locked,target=/var/cache/pacman \
# pacman -Syu --needed ttf-dejavu imagemagick --noconfirm

# RUN find /usr/share/fonts/TTF/* ! -name 'DejaVuSansMono.ttf' -type f -exec rm -f {} + \
    # && fc-cache
RUN useradd  py
WORKDIR /home/py
COPY --chown=py dist/rekdoc .
USER py
CMD ["sh"]
# ENTRYPOINT ["./rekdoc"]
