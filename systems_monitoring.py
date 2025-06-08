from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import os
import platform
import psutil
import time
import argparse

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')


# System Monitoring Functions
# inspired from https://umeey.medium.com/system-monitoring-made-easy-with-pythons-psutil-library-4b9add95a443

def get_kernel_info():
    if hasattr(os, 'uname'):
        uname = os.uname()
        return {
            "kernel_version": uname.release,
            "system_name": uname.sysname,
            "node_name": uname.nodename,
            "machine": uname.machine
        }
    else:
        uname = platform.uname()
        return {
            "kernel_version": uname.release,
            "system_name": uname.system,
            "node_name": uname.node,
            "machine": uname.machine
        }


def get_memory_info():
    return {
        "total_memory": psutil.virtual_memory().total / (1024.0 ** 3),
        "available_memory": psutil.virtual_memory().available / (1024.0 ** 3),
        "used_memory": psutil.virtual_memory().used / (1024.0 ** 3),
        "memory_percentage": psutil.virtual_memory().percent
    }


def get_swap_info():
    swap = psutil.swap_memory()

    return {
        "total_swap": swap.total / (1024.0 ** 3),
        "available_swap": swap.free / (1024.0 ** 3),
        "used_swap": swap.used / (1024.0 ** 3),
        "swap_percentage": swap.percent,
        "swap_in": swap.sin / (1024.0 ** 3),
        "swap_out": swap.sout / (1024.0 ** 3),
    }


def get_cpu_info():
    try:
        cpu_freq = psutil.cpu_freq()
        processor_speed = cpu_freq.current if cpu_freq else None
    except FileNotFoundError:
        processor_speed = "Unavailable on Apple Silicon"

    return {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "processor_speed": processor_speed,
        "cpu_usage_per_core": dict(enumerate(psutil.cpu_percent(percpu=True, interval=1))),
        "total_cpu_usage": psutil.cpu_percent(interval=1)
    }


def get_disk_info_():
    partitions = psutil.disk_partitions()
    disk_info = {}
    for partition in partitions:
        partition_usage = psutil.disk_usage(partition.mountpoint)
        disk_info[partition.mountpoint] = {
            "total_space": partition_usage.total / (1024.0 ** 3),
            "used_space": partition_usage.used / (1024.0 ** 3),
            "free_space": partition_usage.free / (1024.0 ** 3),
            "usage_percentage": partition_usage.percent
        }
    return disk_info


def get_disk_info():
    try:
        usage = psutil.disk_usage('/')
        total = usage.total
        free = usage.free
        used = total - free

        return {
            "/": {
                "total_space": total / (1024.0 ** 3),
                "used_space": used / (1024.0 ** 3),
                "free_space": free / (1024.0 ** 3),
                "usage_percentage": (used / total) * 100
            }
        }
    except Exception as e:
        return {"error": str(e)}


def get_network_info():
    net_io_counters = psutil.net_io_counters()
    return {
        "bytes_sent": net_io_counters.bytes_sent,
        "bytes_recv": net_io_counters.bytes_recv
    }


def get_network_speed(interval=1):
    # get initial network statistics
    net_io_before = psutil.net_io_counters()
    bytes_sent_before = net_io_before.bytes_sent  # upload
    bytes_recv_before = net_io_before.bytes_recv  # download

    time.sleep(interval)  # wait for the specified interval

    # get network statistics after the interval
    net_io_after = psutil.net_io_counters()
    bytes_sent_after = net_io_after.bytes_sent
    bytes_recv_after = net_io_after.bytes_recv

    # calculate upload and download speed
    upload_speed = (bytes_sent_after - bytes_sent_before) / interval
    download_speed = (bytes_recv_after - bytes_recv_before) / interval

    # convert speeds to bytes and kilobytes
    upload_speed_kb = upload_speed / 1024
    download_speed_kb = download_speed / 1024

    return {
        "download_speed_bytes": download_speed,
        "upload_speed_bytes": upload_speed,
        "download_speed_kb": download_speed_kb,
        "upload_speed_kb": upload_speed_kb,
    }


def get_process_info():
    process_info = []
    for process in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
        try:
            process_info.append({
                "pid": process.info['pid'],
                "name": process.info['name'],
                "memory_percent": process.info['memory_percent'],
                "cpu_percent": process.info['cpu_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    filtered = [p for p in process_info if p["cpu_percent"]
                is not None and p["memory_percent"] is not None]
    return sorted(filtered, key=lambda p: p["cpu_percent"], reverse=True)[:5]


def get_load_average():
    load_avg_1, load_avg_5, load_avg_15 = psutil.getloadavg()
    return {
        "load_average_1": load_avg_1,
        "load_average_5": load_avg_5,
        "load_average_15": load_avg_15
    }


def get_disk_io_counters():
    io_counters = psutil.disk_io_counters()
    if io_counters is None:
        return {
            "read_count": 0,
            "write_count": 0,
            "read_bytes": 0,
            "write_bytes": 0,
            "read_time": 0,
            "write_time": 0
        }

    return {
        "read_count": io_counters.read_count,
        "write_count": io_counters.write_count,
        "read_bytes": io_counters.read_bytes,
        "write_bytes": io_counters.write_bytes,
        "read_time": io_counters.read_time,
        "write_time": io_counters.write_time
    }


def get_net_io_counters():
    io_counters = psutil.net_io_counters()
    return {
        "bytes_sent": io_counters.bytes_sent,
        "bytes_recv": io_counters.bytes_recv,
        "packets_sent": io_counters.packets_sent,
        "packets_recv": io_counters.packets_recv,
        "errin": io_counters.errin,
        "errout": io_counters.errout,
        "dropin": io_counters.dropin,
        "dropout": io_counters.dropout
    }


def get_system_uptime():
    boot_time_timestamp = psutil.boot_time()
    current_time_timestamp = time.time()
    uptime_seconds = current_time_timestamp - boot_time_timestamp
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    uptime_days = uptime_hours // 24
    uptime_str = f"{int(uptime_days)} days, {int(uptime_hours % 24)} hours, {int(uptime_minutes % 60)} minutes, {int(uptime_seconds % 60)} seconds"
    return {"uptime": uptime_str}


def get_battery_info():
    battery = psutil.sensors_battery()
    battery_data = {}

    battery_data["battery_percentage"] = battery.percent
    battery_data["power_plugged_in"] = battery.power_plugged

    # battery.secsleft provides the approximate number of seconds left before the battery runs out
    if battery.secsleft == psutil.POWER_TIME_UNKNOWN:
        battery_data["battery_time_left"] = None
    elif battery.secsleft == psutil.POWER_TIME_UNLIMITED:
        battery_data["battery_time_left"] = "Battery is currently being charged."
    else:
        # converting seconds to hours, minutes, and seconds
        hours_left = battery.secsleft // 3600
        minutes_left = (battery.secsleft % 3600) // 60
        seconds_left = (battery.secsleft % 60)
        battery_data["battery_time_left"] = {
            "hours": hours_left, "minutes": minutes_left, "seconds": seconds_left}

    return battery_data

# API App


def create_api_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/api/system_info', methods=['GET'])
    def system_info():
        return jsonify({
            "kernel_info": get_kernel_info(),
            "memory_info": get_memory_info(),
            "swap_info": get_swap_info(),
            "cpu_info": get_cpu_info(),
            "disk_info": get_disk_info(),
            "network_info": get_network_info(),
            "network_speed": get_network_speed(1),
            "process_info": get_process_info(),
            "system_uptime": get_system_uptime(),
            "load_average": get_load_average(),
            "disk_io_counters": get_disk_io_counters(),
            "net_io_counters": get_net_io_counters(),
            "battery_info": get_battery_info(),
        })

    return app

# Frontend App


def create_frontend_app(api_base_url):
    app = Flask(__name__, static_folder=STATIC_DIR)

    @app.route('/')
    def serve_index():
        with open(os.path.join(STATIC_DIR, 'index.html')) as f:
            html_content = f.read()
        injected = f"<script>window.apiBase = '{api_base_url}';</script>"
        return render_template_string(injected + html_content)

    return app


# Main entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='System Monitoring Dashboard',
        epilog='Usages:\n'
               '  python systems_monitoring.py --mode api\n'
               '  python systems_monitoring.py --mode frontend --api-host 192.168.1.100 --api-port 8000\n'
               '  python systems_monitoring.py --mode both --port 8000',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--mode', choices=['api', 'frontend', 'both'],
                        default='both', help='Mode to run: API/Frontend/both')
    parser.add_argument('--port', type=int, default=8000,
                        help='Port to run the server on (default: 8000)')
    parser.add_argument('--api-host', type=str,
                        help='API hostname (used in --mode frontend)')
    parser.add_argument('--api-port', type=int,
                        help='API port (used in --mode frontend)')
    args = parser.parse_args()

    if args.mode == 'api':
        app = create_api_app()

    elif args.mode == 'frontend':
        if not args.api_host or not args.api_port:
            parser.error(
                "When using --mode frontend, you must specify --api-host and --api-port")
        api_url = f"http://{args.api_host}:{args.api_port}"
        app = create_frontend_app(api_url)

    else:
        api_url = f"http://localhost:{args.port}"
        app = create_api_app()
        fe_app = create_frontend_app(api_url)

        @app.route('/')
        def serve_index_combined():
            return fe_app.view_functions['serve_index']()

    app.run(host='0.0.0.0', port=args.port,)
