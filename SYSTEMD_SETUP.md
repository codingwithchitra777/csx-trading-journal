# CSX Trading Journal - Systemd Service Setup

## Overview
This guide explains how to set up the CSX Trading Journal bot as a systemd service so it automatically runs and stays alive on your GitHub server.

## Files Created
- `csx-trading-journal.service` - Systemd service unit file
- `setup-systemd.sh` - Installation script (requires root/sudo)

## Installation

### Step 1: Copy the service file to the project directory
The service file is already in your project directory:
```
/workspaces/csx-trading-journal/csx-trading-journal.service
```

### Step 2: Run the setup script as root
```bash
sudo /workspaces/csx-trading-journal/setup-systemd.sh
```

This script will:
1. Copy the service file to `/etc/systemd/system/`
2. Reload the systemd daemon
3. Enable the service to start on boot
4. Start the service immediately

### Manual Installation (if setup script doesn't work)
```bash
# Copy service file
sudo cp /workspaces/csx-trading-journal/csx-trading-journal.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable on boot
sudo systemctl enable csx-trading-journal

# Start the service
sudo systemctl start csx-trading-journal
```

## Service Management

### Check Status
```bash
sudo systemctl status csx-trading-journal
```

### Start the Service
```bash
sudo systemctl start csx-trading-journal
```

### Stop the Service
```bash
sudo systemctl stop csx-trading-journal
```

### Restart the Service
```bash
sudo systemctl restart csx-trading-journal
```

### View Logs (Last 50 lines)
```bash
journalctl -u csx-trading-journal -n 50
```

### Follow Logs in Real-Time
```bash
journalctl -u csx-trading-journal -f
```

### View Full Service Details
```bash
systemctl show -p Status csx-trading-journal
```

## Service Configuration

### How it works:
- **Type**: `simple` - Bot runs in foreground
- **User**: `codespace` - Runs as codespace user
- **WorkingDirectory**: `/workspaces/csx-trading-journal` - Project directory
- **ExecStart**: Uses Python from virtual environment
- **Restart**: `always` - Automatically restarts on failure
- **RestartSec**: 10 seconds - Waits 10 seconds before restart

### Logs
All output is sent to systemd journal:
```bash
# View recent logs
journalctl -u csx-trading-journal

# View logs from last hour
journalctl -u csx-trading-journal --since "1 hour ago"

# View errors only
journalctl -u csx-trading-journal -p err
```

## Troubleshooting

### Service won't start
Check the logs:
```bash
journalctl -u csx-trading-journal -n 100
```

### Permission denied errors
Ensure the directory permissions are correct:
```bash
sudo chown -R codespace:codespace /workspaces/csx-trading-journal
```

### Python virtual environment not found
Verify the path in the service file matches your actual venv location:
```bash
ls -la /workspaces/csx-trading-journal/py-venv/bin/python
```

### Check if service is enabled
```bash
systemctl is-enabled csx-trading-journal
```

### Check if service is active
```bash
systemctl is-active csx-trading-journal
```

## Enable Auto-Start on Boot

The setup script already does this, but if you need to disable/re-enable:

```bash
# Enable auto-start on boot
sudo systemctl enable csx-trading-journal

# Disable auto-start on boot (but keep running)
sudo systemctl disable csx-trading-journal
```

## Verify Installation

After installation, verify everything is working:

```bash
# Check service is active
sudo systemctl is-active csx-trading-journal

# Should output: active

# Check service is enabled for boot
sudo systemctl is-enabled csx-trading-journal

# Should output: enabled

# Check status
sudo systemctl status csx-trading-journal
```

## Monitoring

To continuously monitor the service:
```bash
# Watch service status every 2 seconds
watch -n 2 systemctl status csx-trading-journal

# Or follow logs in real-time
journalctl -u csx-trading-journal -f
```

## Removing the Service

If you need to remove the service:

```bash
# Stop the service
sudo systemctl stop csx-trading-journal

# Disable auto-start
sudo systemctl disable csx-trading-journal

# Remove the service file
sudo rm /etc/systemd/system/csx-trading-journal.service

# Reload systemd
sudo systemctl daemon-reload
```

## Service File Contents

The service file (`csx-trading-journal.service`) contains:
- Unit description and dependencies
- Service type and execution settings
- Auto-restart configuration
- Logging preferences
- Environment variables
- Installation target for boot

This ensures the bot:
- ✅ Starts automatically on server boot
- ✅ Stays running continuously
- ✅ Automatically restarts if it crashes
- ✅ Logs all output to systemd journal
- ✅ Can be managed with standard systemctl commands

## Quick Reference

```bash
# Installation
sudo /workspaces/csx-trading-journal/setup-systemd.sh

# Daily commands
sudo systemctl status csx-trading-journal          # Check status
sudo systemctl restart csx-trading-journal         # Restart
journalctl -u csx-trading-journal -f              # View logs

# Troubleshooting
journalctl -u csx-trading-journal -n 100          # Last 100 lines
sudo systemctl stop csx-trading-journal           # Stop
sudo systemctl start csx-trading-journal          # Start
```
