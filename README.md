# Manga Site Backend

This repository contains the backend for a manga site, built using FastAPI and PostgreSQL. Comments services using MongoDB and FastAPI. You can easily set up and run the application using Docker Compose.

## Getting Started

To get started with this project, follow the instructions below.

### Prerequisites

Ensure you have Docker and Docker Compose installed on your machine.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Nurshot/manga-backend.git

   cd manga-site-backend
   

2. Compose Up Container:
   ```bash
   docker-compose up --build -d

### Usage

Once the containers are up and running, you can access the FastAPI application at http://localhost:8004

### API Documentation

You can access the automatically generated API documentation at:

	•	Swagger UI: http://localhost:8004/docs
	•	ReDoc: http://localhost:8004/redoc
 
For the comments service:

	•	Swagger UI: http://localhost:8005/docs
	•	ReDoc: http://localhost:8005/redoc
