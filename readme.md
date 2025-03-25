Simple redirect server.

- Pass URL list or a single URL as TARGET_URLS
- Pass URL containing that URL list as URLS_LIST
- Redirect Server will redirect to the first server that responds. Useful for services with multiple instances

Usage:
```yml
version: '3'
services:
  redirect-server:
    build: .
    ports:
      - "5000:5000"
    environment:
      - TARGET_URLS=https://example.com,https://duckduckgo.com
      - URLS_LIST=https://api.invidious.io
```