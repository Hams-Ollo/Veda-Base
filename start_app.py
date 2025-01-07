import subprocess
import time
import webbrowser
import sys
import os
from pathlib import Path
import threading
import socket
import signal
import psutil

def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill the process using the specified port"""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"🔪 Killing process {proc.info['pid']} using port {port}")
                    if sys.platform == "win32":
                        subprocess.run(['taskkill', '/F', '/PID', str(proc.info['pid'])], capture_output=True)
                    else:
                        os.kill(proc.info['pid'], signal.SIGTERM)
                    time.sleep(1)  # Give the process time to die
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def print_output(process, prefix):
    """Print the output of a process with a prefix"""
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(f"{prefix}: {line.strip()}")
    while True:
        line = process.stderr.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(f"❌ {prefix} ERROR: {line.strip()}")

def find_npm():
    """Find the npm executable based on the operating system"""
    print("🔍 Looking for npm executable...")
    if sys.platform == "win32":
        # Try common Windows npm locations
        npm_paths = [
            r"C:\Program Files\nodejs\npm.cmd",
            r"C:\Program Files (x86)\nodejs\npm.cmd",
            os.path.expandvars(r"%APPDATA%\npm\npm.cmd"),
            os.path.expandvars(r"%ProgramFiles%\nodejs\npm.cmd"),
            "npm.cmd"  # Try PATH
        ]
        for npm_path in npm_paths:
            if os.path.exists(npm_path):
                print(f"✅ Found npm at: {npm_path}")
                return npm_path
        raise FileNotFoundError("❌ npm not found. Please ensure Node.js is installed and in your PATH")
    return "npm"  # For non-Windows systems

def start_backend():
    """Start the FastAPI backend server"""
    print("\n🚀 Starting backend server...")
    # Check if port 8000 is in use
    if is_port_in_use(8000):
        print("⚠️  Port 8000 is in use. Attempting to kill existing process...")
        if not kill_process_on_port(8000):
            print("❌ Could not kill process on port 8000")
            sys.exit(1)

    try:
        print("📡 Starting uvicorn server on port 8000...")
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        # Start thread to print backend output
        threading.Thread(target=print_output, args=(backend_process, "Backend"), daemon=True).start()
        return backend_process
    except Exception as e:
        print(f"❌ Error starting backend: {str(e)}")
        sys.exit(1)

def start_frontend():
    """Start the Next.js frontend server"""
    print("\n🌐 Starting frontend server...")
    # Check if port 3000 is in use
    if is_port_in_use(3000):
        print("⚠️  Port 3000 is in use. Attempting to kill existing process...")
        if not kill_process_on_port(3000):
            print("❌ Could not kill process on port 3000")
            sys.exit(1)

    try:
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            raise FileNotFoundError(f"❌ Frontend directory not found at {frontend_dir}")

        # First install dependencies if needed
        print("📦 Checking frontend dependencies...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True, shell=True)

        print("🚀 Starting Next.js development server...")
        npm_cmd = find_npm()
        frontend_process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1,
            shell=True
        )
        # Start thread to print frontend output
        threading.Thread(target=print_output, args=(frontend_process, "Frontend"), daemon=True).start()
        return frontend_process
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing frontend dependencies: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting frontend: {str(e)}")
        sys.exit(1)

def check_server_health(url, timeout=30, allow_404=False):
    """Check if a server is responding"""
    import urllib.request
    import urllib.error
    print(f"🏥 Checking health of {url}")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = urllib.request.urlopen(url)
            print(f"✅ {url} is healthy")
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404 and allow_404:
                # For Next.js, a 404 response still means the server is running
                print(f"✅ {url} is responding (404 allowed)")
                return True
            time.sleep(1)
        except urllib.error.URLError:
            print("⏳ Waiting for server to respond...")
            time.sleep(1)
    print(f"❌ Health check failed for {url}")
    return False

def wait_for_frontend_ready(frontend_process, timeout=30):
    """Wait for Next.js to be ready by monitoring its output"""
    print("⏳ Waiting for Next.js to be ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if frontend_process.poll() is not None:
            print("❌ Frontend process ended unexpectedly")
            return False
        output = frontend_process.stdout.readline()
        if output:
            if "Ready" in output:
                print("✅ Next.js is ready!")
                return True
        time.sleep(0.1)
    print("❌ Timeout waiting for Next.js")
    return False

def main():
    print("\n🚀 Starting Library of Alexandria Development Environment\n")
    
    # Start backend
    backend_process = start_backend()
    print("\n⏳ Waiting for backend to start...")
    if not check_server_health("http://localhost:8000/api/health", timeout=30):
        print("❌ Backend failed to start properly")
        backend_process.terminate()
        sys.exit(1)
    print("✅ Backend is running!")

    # Start frontend
    frontend_process = start_frontend()
    print("\n⏳ Waiting for frontend to start...")
    
    # Wait for Next.js to be ready
    if not wait_for_frontend_ready(frontend_process):
        print("❌ Frontend failed to start properly")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(1)
    print("✅ Frontend is running!")

    # Open browser
    print("\n🌐 Opening browser...")
    webbrowser.open("http://localhost:3000")
    print("✅ Development environment is ready!")
    print("\n💡 Press Ctrl+C to stop all servers\n")

    try:
        # Keep the script running
        while True:
            if backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                frontend_process.terminate()
                sys.exit(1)
            if frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                backend_process.terminate()
                sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down development environment...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ All servers stopped successfully")
        sys.exit(0)

if __name__ == "__main__":
    main() 