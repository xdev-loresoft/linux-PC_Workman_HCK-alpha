### xdev - 26.03.2026 for 1.6.8 - 

import sys
import time
from typing import Optional, Any


def log(msg: str, level: str = "INFO"):
    prefix = {
        "INFO": "[*]",
        "OK": "[+]",
        "WARN": "[!]",
        "ERROR": "[-]",
        "LOAD": "[~]"
    }.get(level, "[*]")
    print(f"{prefix} {msg}")


def run():
    print("=" * 70)
    print("  PC Workman (Linux Alpha)")
    print("=" * 70)
    print()

    log("Initializing environment...", "LOAD")

    try:
        from import_core import COMPONENTS, count_components
        log("import_core loaded", "OK")
    except Exception as e:
        log(f"import_core FAILED: {e}", "ERROR")
        return

    log("Loading core modules...", "LOAD")

    core_ok = True
    for module in [
        "core.monitor",
        "core.logger",
        "core.analyzer",
        "core.scheduler"
    ]:
        try:
            __import__(module)
        except Exception as e:
            log(f"{module} FAILED: {e}", "ERROR")
            core_ok = False

    if core_ok:
        log("Core modules loaded", "OK")

    try:
        import core.process_classifier
        import core.process_data_manager
    except Exception:
        pass

    log("Loading Stats Engine v2...", "LOAD")

    stats_ready = False
    try:
        from hck_stats_engine import db_manager
        if db_manager.is_ready:
            stats_ready = True
            log("Stats Engine ready", "OK")
        else:
            log("Stats Engine loaded (DB not ready)", "WARN")
    except Exception as e:
        log(f"Stats Engine FAILED: {e}", "ERROR")

    log(f"Components: {count_components()}", "INFO")

    scheduler = COMPONENTS.get("core.scheduler")
    monitor = COMPONENTS.get("core.monitor")
    logger = COMPONENTS.get("core.logger")

    if monitor and hasattr(monitor, "start_background_collection"):
        monitor.start_background_collection(interval=1.0)
        log("Monitor started", "OK")

    if scheduler:
        try:
            scheduler.start_loop()
            log("Scheduler started", "OK")
        except Exception as e:
            log(f"Scheduler FAILED: {e}", "ERROR")
            scheduler = None

    log("Starting UI...", "LOAD")

    HAS_UI = False
    main_window = None

    try:
        import ui.windows.main_window_expanded as main_window
        HAS_UI = True
        log("UI loaded", "OK")
    except Exception as e:
        log(f"UI FAILED: {e}", "WARN")

    if HAS_UI and main_window:
        try:
            window = main_window.ExpandedMainWindow(
                data_manager=COMPONENTS.get("core.process_data_manager"),
                monitor=monitor,
                switch_to_minimal_callback=lambda: None,
                quit_callback=lambda: None
            )
            log("UI running", "OK")
            window.run()
        except Exception as e:
            log(f"UI crash: {e}", "ERROR")
    else:
        log("Headless mode", "WARN")
        time.sleep(5)

        if logger:
            try:
                samples = logger.get_last_n_samples(5)
                for s in samples:
                    print(
                        f"CPU: {s['cpu_percent']}% "
                        f"RAM: {s['ram_percent']}% "
                        f"GPU: {s['gpu_percent']}%"
                    )
            except Exception:
                pass

    if scheduler:
        try:
            scheduler.stop()
        except Exception:
            pass

    try:
        from hck_stats_engine.aggregator import aggregator
        aggregator.flush_on_shutdown()
    except Exception:
        pass

    try:
        from hck_stats_engine.db_manager import db_manager
        db_manager.close()
    except Exception:
        pass


if __name__ == "__main__":
    run()
