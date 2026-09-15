FROM python:3.12-slim
RUN adduser --disabled-password --gecos '' appuser
WORKDIR /app
COPY rangyuu rangyuu
COPY entrypoint.py .
ENV PORT=8080
EXPOSE 8080
USER appuser
CMD ["python","entrypoint.py"]
