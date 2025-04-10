import multiprocessing
import os

# Bind to the port provided by Render
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker configuration - adjust based on instance size
workers = int(os.environ.get('WEB_CONCURRENCY', multiprocessing.cpu_count() * 2 + 1))
# worker_class = "gevent" # Uncomment and add gevent to requirements.txt if needed
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "nyure_education" # Renamed for consistency

# Server hooks
def on_starting(server):
    server.log.info("Starting Course Compass server")

def on_exit(server):
    server.log.info("Stopping Course Compass server")

# Max requests per worker before restart
max_requests = 1000
max_requests_jitter = 50

# Preload app for faster worker startup
preload_app = True
