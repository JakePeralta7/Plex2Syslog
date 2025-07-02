# Plex2Syslog

Forward Plex webhooks to syslog.

## Quick Start

### Using Docker Compose

1. Create a `docker-compose.yml` file:
```yaml
services:
  plex2syslog:
    image: ghcr.io/your-username/plex2syslog:latest
    container_name: plex2syslog
    ports:
      - "8080:8080"
    environment:
      - HOST=0.0.0.0
      - PORT=8080
      - SYSLOG_HOST=your-syslog-server.local
      - SYSLOG_PORT=514
      - SYSLOG_FACILITY=LOCAL0
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

2. Start the container:
```bash
docker-compose up -d
```

3. Configure Plex webhook URL: `http://your-server:8080/webhook`

### Building from Source

1. Clone this repository:
```bash
git clone https://github.com/your-username/Plex2Syslog.git
cd Plex2Syslog
```

2. Build and run:
```bash
docker build -t plex2syslog .

docker run -d \
  --name plex2syslog \
  -p 8080:8080 \
  -e SYSLOG_HOST=your-syslog-server \
  -e SYSLOG_PORT=514 \
  -e SYSLOG_FACILITY=LOCAL0 \
  plex2syslog
```

## Available Images

Images are automatically built and published to GitHub Container Registry:

- `ghcr.io/your-username/plex2syslog:latest` - Latest stable release
- `ghcr.io/your-username/plex2syslog:main` - Latest development build
- `ghcr.io/your-username/plex2syslog:v1.0.0` - Specific version tags

## Configuration

Configure the application using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Interface to bind to | `0.0.0.0` |
| `PORT` | Port to listen on | `8080` |
| `SYSLOG_HOST` | Syslog server hostname/IP | `localhost` |
| `SYSLOG_PORT` | Syslog server port | `514` |
| `SYSLOG_FACILITY` | Syslog facility | `LOCAL0` |
| `LOG_LEVEL` | Application log level | `INFO` |

### Syslog Facilities

Available syslog facilities:
- `LOCAL0` through `LOCAL7`
- `USER`, `MAIL`, `DAEMON`, `AUTH`, `SYSLOG`, `LPR`, `NEWS`, `UUCP`, `CRON`, `AUTHPRIV`

## Plex Configuration

1. In Plex Media Server, go to Settings → Webhooks
2. Add a new webhook with URL: `http://your-server:8080/webhook`
3. Select the events you want to monitor

## API Endpoints

- `POST /webhook` - Receives Plex webhooks
- `GET /health` - Health check endpoint
- `GET /` - Service information

## Syslog Message Format

Messages are formatted as:
```
Plex2Syslog: Event: media.play | User: john | Server: PlexServer | Media: Movie Title (movie) | Player: Living Room TV
```

## Example Events

Common Plex events that will be forwarded:
- `media.play` - Media playback started
- `media.pause` - Media playback paused
- `media.resume` - Media playback resumed
- `media.stop` - Media playback stopped
- `media.scrobble` - Media finished playing
- `library.new` - New media added to library

## Monitoring

Check container health:
```bash
docker ps
curl http://localhost:8080/health
```

View logs:
```bash
docker logs plex2syslog
```

## Development

Run locally for development:
```bash
pip install -r requirements.txt
export SYSLOG_HOST=localhost
python app.py
```

### Building Multi-Architecture Images

The GitHub workflow automatically builds for multiple architectures. To build locally:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t plex2syslog .
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

- Create an issue for bug reports or feature requests
- Check the logs for troubleshooting: `docker logs plex2syslog`
- Verify syslog connectivity with your target server

