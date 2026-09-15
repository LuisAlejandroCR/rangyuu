FROM python:3.12-slim
WORKDIR /app
COPY rangyuu rangyuu
COPY entrypoint.py .
ENV PORT=8080
EXPOSE 8080
CMD ["python","entrypoint.py"]
