# Docker Configuration

This folder contains Docker configuration files for development and testing environments.

## 📁 Files to Create Here

| File | Description | Owner |
|------|-------------|-------|
| `docker-compose.yml` | Main orchestration file | Backend/DevOps |
| `docker-compose.dev.yml` | Development overrides | Backend |
| `docker-compose.test.yml` | Testing environment | Backend/QA |
| `.env.example` | Docker environment template | Backend |

## 🐳 Services to Containerize

| Service | Port | Description |
|---------|------|-------------|
| backend | 5000 | Flask API |
| frontend | 5173 | React/Vite dev server |
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Caching & rate limiting |

## 📍 Dockerfile Locations

Dockerfiles live with their respective services:
- `backend/Dockerfile` - Flask backend image
- `frontend/Dockerfile` - React frontend image

## 🚀 Usage (Once Files Are Created)

```bash
# Development
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up

# Testing
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.test.yml up

# Build only
docker-compose -f docker/docker-compose.yml build
```

## 👥 Owners

| Role | Name |
|------|------|
| Backend | Ariel, Suryadi |
| Frontend | Joseph, Jae Young |
| DevOps/CS | Monira |

---

## 📚 Learning Resources

New to Docker? Here are some resources to get started:

### Official Documentation
- [Docker Get Started Guide](https://docs.docker.com/get-started/) - Official beginner tutorial
- [Docker Compose Documentation](https://docs.docker.com/compose/) - Multi-container orchestration
- [Dockerfile Reference](https://docs.docker.com/reference/dockerfile/) - Building images

### Video Tutorials
- [Docker Tutorial for Beginners (TechWorld with Nana)](https://www.youtube.com/watch?v=3c-iBn73dDE) - 3hr comprehensive course
- [Docker Crash Course (Traversy Media)](https://www.youtube.com/watch?v=Kyx2PsuwomE) - 1hr quick intro
- [Docker Compose Tutorial (NetworkChuck)](https://www.youtube.com/watch?v=DM65_JyGxCo) - Fun beginner-friendly

### Interactive Learning
- [Docker Labs (Play with Docker)](https://labs.play-with-docker.com/) - Free browser-based Docker environment
- [Docker 101 Tutorial](https://www.docker.com/101-tutorial/) - Official hands-on tutorial

### Cheat Sheets
- [Docker CLI Cheat Sheet](https://docs.docker.com/get-started/docker_cheatsheet.pdf) - Official PDF
- [Docker Compose Cheat Sheet](https://devhints.io/docker-compose) - Quick reference

### Flask + Docker Specific
- [Dockerizing Flask with Postgres](https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/) - Great for our stack
- [Flask Docker Best Practices](https://pythonspeed.com/docker/)
