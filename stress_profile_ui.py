import subprocess
import threading
import time
import psutil

LOG_INTERVAL = 0.5  # secondes

mem_peaks = []
cpu_peaks = []
start_time = time.time()

proc = subprocess.Popen(['python', 'stress_test_ui.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
ps_proc = psutil.Process(proc.pid)

def monitor():
    while proc.poll() is None:
        try:
            mem = ps_proc.memory_info().rss / (1024*1024)  # MB
            cpu = ps_proc.cpu_percent(interval=None)
            mem_peaks.append(mem)
            cpu_peaks.append(cpu)
        except Exception:
            pass
        time.sleep(LOG_INTERVAL)

mon_thread = threading.Thread(target=monitor)
mon_thread.start()
out, _ = proc.communicate()
mon_thread.join()
end_time = time.time()

total_time = end_time - start_time
max_mem = max(mem_peaks) if mem_peaks else 0
max_cpu = max(cpu_peaks) if cpu_peaks else 0

print(f"[PROFILE] Temps total : {total_time:.2f}s")
print(f"[PROFILE] Pic mémoire : {max_mem:.2f} MB")
print(f"[PROFILE] Pic CPU : {max_cpu:.2f} %")
print("\n--- Extrait de log ---\n")
print(out[-2000:] if out else "") 