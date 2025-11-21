# Downes Agent Web Interface

This is a simple web interface for the Downes Agent.

## Prerequisites

- Node.js installed
- Python environment set up (via `uv`)

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

## Running

1. Start the server:

   ```bash
   npm start
   ```

2. Open your browser at [http://localhost:3000](http://localhost:3000).

## Architecture

The web server (`server.js`) serves a static HTML page (`public/index.html`) and listens for WebSocket connections.
When a user submits a query, the server spawns a Python process running `src/downes/web_adapter.py`.
This Python script initializes the `Agent` with a custom `WebUI` that emits JSON events to stdout.
The Node.js server parses these JSON events and forwards them to the frontend via Socket.IO.
The frontend renders the events as a chat interface.
