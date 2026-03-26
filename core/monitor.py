### xdev - linux - for PC Workman 1.6.8
from import_core import register_component
import time
import threading
import psutil
import platform
import os

try:
    import GPUtil
    _GPUS_AVAILABLE = True
except Exception:
    _GPUS_AVAILABLE = False


class Monitor:
    def __init__(self):
        self.name = "core.monitor"
        self._cached_snapshot = None
        self._snapshot_lock = threading.Lock()
        self._bg_running = False
        register_component(self.name, self)

    def start_background_collection(self, interval=1.0):
        if self._bg_running:
            return
        self._bg_running = True
        self._bg_interval = interval
        t = threading.Thread(target=self._bg_collect_loop, daemon=True)
        t.start()
        print("[Monitor] Background collection started")

    def stop_background_collection(self):
        self._bg_running = False

    def _bg_collect_loop(self):
        while self._bg_running:
            try:
                snap = self._collect_snapshot()
                with self._snapshot_lock:
                    self._cached_snapshot = snap
            except Exception as e:
                print(f"[Monitor] BG collection error: {e}")
            time.sleep(self._bg_interval)

    def _get_gpu_percent(self):
        if _GPUS_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    vals = [g.load * 100.0 for g in gpus]
                    return round(sum(vals) / len(vals), 2)
            except Exception:
                pass

        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                vals = [float(x) for x in result.stdout.strip().split("\n") if x]
                if vals:
                    return round(sum(vals) / len(vals), 2)
        except Exception:
            pass

        return 0.0

    def _get_linux_temp(self):
        try:
            thermal_path = "/sys/class/thermal"
            temps = []
            for entry in os.listdir(thermal_path):
                zone_path = os.path.join(thermal_path, entry, "temp")
                if os.path.isfile(zone_path):
                    with open(zone_path, "r") as f:
                        val = int(f.read().strip()) / 1000.0
                        temps.append(val)
            if temps:
                return round(max(temps), 2)
        except Exception:
            pass
        return 0.0

    def _get_load_avg(self):
        try:
            if hasattr(os, "getloadavg"):
                load1, _, _ = os.getloadavg()
                return round(load1, 2)
        except Exception:
            pass
        return 0.0

    def _collect_snapshot(self):
        ts = time.time()
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        gpu = self._get_gpu_percent()

        system = platform.system()

        cpu_temp = 0.0
        load_avg = 0.0

        if system == "Linux":
            cpu_temp = self._get_linux_temp()
            load_avg = self._get_load_avg()

        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                info = p.info
                cpu_p = info.get('cpu_percent') or 0.0
                mem_info = info.get('memory_info')
                ram_mb = (mem_info.rss / (1024 * 1024)) if mem_info else 0.0

                procs.append({
                    'pid': info.get('pid'),
                    'name': (info.get('name') or '').strip(),
                    'cpu_percent': round(cpu_p, 2),
                    'ram_MB': round(ram_mb, 2)
                })

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return {
            'timestamp': ts,
            'cpu_percent': round(cpu, 2),
            'ram_percent': round(ram, 2),
            'gpu_percent': round(gpu, 2),
            'cpu_temp': cpu_temp,
            'load_avg': load_avg,
            'processes': procs
        }

    def read_snapshot(self):
        with self._snapshot_lock:
            if self._cached_snapshot is not None:
                return self._cached_snapshot
        return self._collect_snapshot()

    def top_processes(self, n=6, by='cpu'):
        snap = self.read_snapshot()
        procs = snap.get('processes', [])

        if by == 'ram':
            key = lambda p: p.get('ram_MB', 0.0)
        elif by == 'cpu+ram':
            key = lambda p: (
                p.get('cpu_percent', 0.0) + (p.get('ram_MB', 0.0) / 1024.0)
            )
        else:
            key = lambda p: p.get('cpu_percent', 0.0)

        procs_sorted = sorted(procs, key=key, reverse=True)
        return procs_sorted[:n]


monitor = Monitor()
