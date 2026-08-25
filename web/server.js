const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const { spawn } = require('child_process');
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

app.use(express.static(path.join(__dirname, 'public')));

io.on('connection', (socket) => {
    console.log('A user connected');

    socket.on('run_agent', (query) => {
        console.log(`Running agent with query: ${query}`);

        const scriptPath = path.join(__dirname, '../src/downes/web_adapter.py');

        // Use 'uv' to run python in the correct environment
        const pythonProcess = spawn('uv', ['run', 'python', scriptPath, query], {
            cwd: path.join(__dirname, '..'),
            env: process.env
        });

        let buffer = '';

        pythonProcess.stdout.on('data', (data) => {
            buffer += data.toString();
            const lines = buffer.split('\n');

            // The last element is either empty (if data ended with \n)
            // or an incomplete line. We keep it in the buffer.
            buffer = lines.pop();

            for (const line of lines) {
                if (line.trim()) {
                    try {
                        const json = JSON.parse(line);
                        socket.emit('agent_event', json);
                    } catch (e) {
                        // If it's not JSON, just emit as raw log
                        // console.log('Non-JSON output:', line);
                        socket.emit('agent_event', { type: 'raw', data: line });
                    }
                }
            }
        });

        pythonProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
            // socket.emit('agent_event', { type: 'error', data: { message: data.toString() } });
        });

        pythonProcess.on('close', (code) => {
            if (buffer.trim()) {
                try {
                    const json = JSON.parse(buffer);
                    socket.emit('agent_event', json);
                } catch (e) {
                    socket.emit('agent_event', { type: 'raw', data: buffer });
                }
            }
            console.log(`child process exited with code ${code}`);
            socket.emit('agent_event', { type: 'done', data: { code } });
        });
    });

    socket.on('disconnect', () => {
        console.log('User disconnected');
    });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
