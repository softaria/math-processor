FROM python
RUN groupadd -g 999 appuser && \
    useradd -r -u 999 -g appuser appuser
RUN python --version
RUN pip install sympy
RUN pip install Flask
RUN pip install matplotlib
USER appuser
COPY src /src

EXPOSE 5000

CMD python /src/server.py
