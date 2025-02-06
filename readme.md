Simple redirect server.

Usage:
```yml
version: '3'
services:
  redirect-server:
    image: matszwe02/redirect-server:latest
    # build: .
    ports:
      - "8080:80"
    environment:
      - TARGET_URL=https://libreddit.eu.org
```