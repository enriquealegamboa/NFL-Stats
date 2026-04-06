# NFL Data Backend API

A backend system that collects, stores, and serves NFL data through a REST API.
This project demonstrates backend development, database design, and data engineering using real NFL data sourced from the ESPN API.

The goal of the project is to build a **production-style backend service** that can power analytics, dashboards, or sports applications.

---

## Project Overview

This project builds a **complete NFL data backend** consisting of:

* Data ingestion from the ESPN API
* Relational database schema for NFL entities
* Backend REST API built with ASP.NET Core
* Cloud-hosted PostgreSQL database using Supabase
* Python scripts for data collection and ETL

The system stores structured NFL data including:

* Teams
* Players
* Games
* Seasons
* Player statistics
* Team statistics

---

## Architecture

<img width="717" height="67" alt="Architecture" src="https://github.com/user-attachments/assets/2c430fe1-32c1-4b9c-b838-00169beb4128" />

---

## Tech Stack

### Backend

* ASP.NET Core Web API
* Swagger / OpenAPI

### Database

* Supabase (PostgreSQL)
* Relational schema designed using EER modeling

### Data Engineering

* Python
* requests
* pandas

### Data Source

* ESPN NFL API

---

## Database Design

The database was designed using an **Enhanced Entity Relationship (EER) model** to represent real NFL relationships.

Core tables include:

| Table        | Description                   |
| :------------ | :----------------------------- |
| teams        | NFL team information          |
| players      | Player roster data            |
| games        | NFL games by season and week  |
| seasons      | NFL seasons                   |
| season_player_stats | Player performance statistics |
| season_team_stats   | Aggregated team statistics    |
| game_team_stats   | team statistics for a single game    |
| season_player_stats | Player performance statistics |
| player_team_stats   |  player stats in game  |

---

## API Endpoints (Planned)

Example endpoints exposed by the backend:

```
GET /teams
GET /teams/{id}

GET /players
GET /players/{id}

GET /games
GET /games/{season}/{week}

GET /stats/team/{teamId}
GET /stats/player/{playerId}
```

Swagger UI is included for easy API testing.

---

## Data Collection

Python scripts pull data from the ESPN API and load it into the Supabase PostgreSQL database.

Example workflow:

```
1. Pull season stats for teams
2. Pull game stats
3. Pull player season stats 
4. Transform data using pandas
5. Insert into Supabase PostgreSQL tables
```

Libraries used:

* requests
* pandas
* supabase 

---

## Features

* RESTful API for NFL data
* Cloud-hosted PostgreSQL database (Supabase)
* Normalized relational schema
* Real NFL data ingestion
* Swagger API documentation
* Designed for scalability

---

## Future Improvements

* Add player game statistics
* Injury report ingestion
* Game prediction model
* Caching layer (Redis)
* Docker deployment
* Authentication

---

## Learning Objectives

This project demonstrates skills in:

* Backend development
* API design
* Database modeling
* ETL pipelines
* Working with third-party APIs
* Cloud database management

---

## How to Run the Project
This project is still in development and is not yet ready to be executed.

## Author

Enrique Gamboa

Backend Development | Data Engineering | Database Design
