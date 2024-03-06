FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run as non-root user for security
RUN useradd -m user
RUN chown -R user:user /app
USER user


ENV PORT=9000
ENV ADMIN_MODE=0
ENV PYTHONPATH=.
ENV BACKEND_URL=http://localhost:8000/


EXPOSE $PORT

COPY . ./frontend

CMD python -m streamlit run frontend/front.py --server.port $PORT