FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run as non-root user for security
RUN useradd -m user
RUN chown -R user:user /app
USER user


ENV PORT=8000
ENV ADMIN_MODE=0
ENV PYTHONPATH=.
ENV DATABASE_URL=sqlite:///db/rag.sqlite3


EXPOSE $PORT

COPY . ./backend

CMD python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT