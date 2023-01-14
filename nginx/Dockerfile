FROM nginx:1.23.3-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY kirovcvetok.ru.crt /etc/nginx/ssl/
COPY kirovcvetok.ru.key /etc/nginx/ssl/
COPY ca.crt /etc/nginx/ssl/

