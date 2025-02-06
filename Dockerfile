FROM nginx:alpine

# Install envsubst
RUN apk add --no-cache gettext

# Copy the Nginx configuration template
COPY nginx.conf.template /etc/nginx/nginx.conf.template

# Create a script to generate the final Nginx configuration
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

# Expose port 80
EXPOSE 80

# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]