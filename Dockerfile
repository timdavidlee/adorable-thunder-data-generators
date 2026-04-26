FROM postgres:16-alpine

ENV POSTGRES_DB=adorable_thunder
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

EXPOSE 5432
