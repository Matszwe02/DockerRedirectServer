# Simple redirect server.

Redirects url to external domain, keeping original path

- Pass URL list or a single URL as TARGET_URLS
- Pass URL containing that URL list as URLS_LIST
- Redirect Server will redirect to the first server that responds. Useful for services with multiple instances

## Behaviour:
Requests are split by groups of 4.
- Checking cached url (last working url, cache valid for 10min)
  - returns if possible
- Checking urls provided by TARGET_URLS
  - returns if possible
- Checking urls provided by URLS_LIST
  - returns if possible
- returns error otherwise

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