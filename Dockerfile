FROM python:3.11-slim as backend
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

FROM node:18-alpine as frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --legacy-peer-deps
COPY frontend ./frontend
WORKDIR /app/frontend
RUN npm run build

FROM python:3.11-slim
WORKDIR /app
# Copy backend python packages (approximation)
COPY --from=backend /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend /app /app
# Copy frontend build to template/static folder (so you can serve static assets if needed)
COPY --from=frontend-build /app/frontend/build /app/templates/_frontend_build
EXPOSE 5000
CMD ["python", "app.py"]
