#!/usr/bin/env python
"""
StockFlow Launcher - Universal startup script for all platforms.
Run this to automatically set up and start the inventory management system.
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path


def run_command(cmd, description, show_output=False):
    """Run a shell command and handle errors."""
    try:
        if show_output:
            result = subprocess.run(cmd, shell=True, check=True)
        else:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False


def main():
    print("\n" + "=" * 50)
    print("  STOCKFLOW - Inventory Management System")
    print("=" * 50 + "\n")

    # Get the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    # Determine Python executable
    python_exe = sys.executable

    # Step 1: Create virtual environment if it doesn't exist
    venv_path = project_root / "venv"
    if not venv_path.exists():
        print("Creating virtual environment...")
        if not run_command(f'"{python_exe}" -m venv venv', "Virtual environment created"):
            sys.exit(1)

    # Step 2: Activate virtual environment and get pip path
    if sys.platform == "win32":
        venv_python = venv_path / "Scripts" / "python.exe"
        venv_pip = venv_path / "Scripts" / "pip.exe"
    else:
        venv_python = venv_path / "bin" / "python"
        venv_pip = venv_path / "bin" / "pip"

    # Step 3: Install requirements
    print("Installing dependencies...")
    if not run_command(f'"{venv_pip}" install -r requirements.txt -q', "Dependencies installed"):
        sys.exit(1)

    # Step 4: Run migrations
    print("Setting up database...")
    if not run_command(f'"{venv_python}" manage.py migrate --noinput', "Database migrations applied"):
        sys.exit(1)

    # Step 5: Check if superuser exists
    print("Checking admin user...")
    check_user_cmd = f'"{venv_python}" -c "from django.contrib.auth import get_user_model; User = get_user_model(); exit(0 if User.objects.filter(is_superuser=True).exists() else 1)"'
    result = subprocess.run(check_user_cmd, shell=True, capture_output=True)
    
    if result.returncode != 0:
        print("\nNo admin user found. Create one now:")
        print("-" * 50)
        subprocess.run(f'"{venv_python}" manage.py createsuperuser', shell=True)

    # Step 6: Summary and start server
    print("\n" + "=" * 50)
    print("  Starting StockFlow...")
    print("=" * 50)
    print("\n✓ Dashboard:   http://127.0.0.1:8000/")
    print("✓ Admin:      http://127.0.0.1:8000/admin/")
    print("\nPress CTRL+C to stop the server\n")

    # Open browser
    time.sleep(2)
    try:
        webbrowser.open("http://127.0.0.1:8000/")
    except Exception:
        pass  # Browser open is optional

    # Start the development server
    subprocess.run(f'"{venv_python}" manage.py runserver', shell=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
        sys.exit(0)
