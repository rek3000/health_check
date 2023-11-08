FROM debian:experimental
# RUN echo deb https://deb.debian.org/debian experimental main >> /etc/apt/sources.list
RUN apt update -y
RUN apt -t experimental install --no-install-recommends libc6 -y
RUN apt clean && rm -rf /var/lib/apt/lists/*
# RUN --mount=type=cache,sharing=locked,target=/var/cache/pacman \
# pacman -Syu --needed ttf-dejavu imagemagick --noconfirm

# RUN find /usr/share/fonts/TTF/* ! -name 'DejaVuSansMono.ttf' -type f -exec rm -f {} + \
    # && fc-cache
RUN useradd  py
WORKDIR /home/py
COPY --chown=py dist/rekdoc .
USER py
CMD ["bash"]
# ENTRYPOINT ["./rekdoc"]
