# Project Garud 🦅

A security-focused, two-container application deployed on AWS EC2 using Docker — featuring reverse proxy request filtering, real-time Telegram attack alerts, and a Flask backend.

## Architecture

Internet → garud-perimeter (Reverse Proxy) → garud-shield (Flask + Gunicorn)

- **garud-perimeter**: Filters incoming requests for malicious patterns, sends real-time alerts via Telegram Bot API
- **garud-shield**: Core Flask application with a voice interface, runs internally on 127.0.0.1:8080

## Features
- Reverse proxy request filtering (blocks path traversal, common attack patterns like ../../etc/passwd)
- Real-time Telegram alerts on blocked attack attempts
- IP ban system with persistence
- Structured JSON logging
- Flask + Gunicorn backend, isolated on internal network

## Tech Stack
Python, Flask, Gunicorn, Docker, AWS EC2, Telegram Bot API, Linux/Ubuntu

## Challenges Solved
- Fixed Docker `--net=host` port-binding conflicts
- Resolved a critical `.env` exposure vulnerability (token rotation + keyword blocking)
- Debugged Flask template path issues in containerized environment
- Fixed JavaScript Web Speech API nested array bug in voice interface

## Note
Personal learning project — not a commercial security product.
