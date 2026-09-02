# AI Linux Command Assistant — Docker Setup

## Requirements
- Docker Desktop installed
- Docker Compose installed
- 10 GB free disk space (for AI model)

## Quick Start (3 commands only)

### Step 1 — Clone or copy project folder
cd AI_command_assistant

### Step 2 — Build and start
docker-compose up --build

### Step 3 — Open in browser
http://localhost:6080
VNC Password: aiassist

## That's it! The app will appear in your browser.

---

## Stopping the app
docker-compose down

## Restart without rebuilding
docker-compose up

## View logs
docker-compose logs -f

## Pull a different AI model
docker exec -it ollama ollama pull mistral

## Change VNC password
Edit docker-compose.yml → VNC_PASSWORD=yournewpassword

## Change screen resolution
Edit docker-compose.yml → VNC_RESOLUTION=1920x1080

---

## Accessing the app

| Method          | URL / Address              | Notes              |
|-----------------|----------------------------|--------------------|
| Browser (noVNC) | http://localhost:6080      | Recommended        |
| VNC Client      | localhost:5901             | Use VNC Viewer app |
| VNC Password    | aiassist                   | Change in compose  |

---

## Ports used

| Port | Service        |
|------|----------------|
| 6080 | noVNC browser  |
| 5901 | VNC direct     |
| 11434| Ollama API     |

---

## Data persistence

| Data           | Stored In         |
|----------------|-------------------|
| AI Models      | ollama_models vol |
| Favorites DB   | app_data volume   |
| Command History| app_data volume   |
| Settings       | app_data volume   |

Data survives container restarts automatically.
