import subprocess
import threading
import time

NB_INSTANCES = 3  # Peut être augmenté à 5 pour un test plus extrême

results = []
logs = []

def run_instance(idx):
    print(f"[CHARGE] Lancement instance {idx+1}")
    proc = subprocess.Popen(['python', 'stress_test_ui.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out, _ = proc.communicate()
    logs.append((idx, out))
    results.append((idx, proc.returncode))
    print(f"[CHARGE] Instance {idx+1} terminée avec code {proc.returncode}")

def main():
    threads = []
    for i in range(NB_INSTANCES):
        t = threading.Thread(target=run_instance, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(1)  # Décalage pour éviter un lancement strictement simultané
    for t in threads:
        t.join()
    print("\n=== Résumé des tests de charge ===")
    for idx, code in results:
        print(f"Instance {idx+1}: {'OK' if code == 0 else 'ECHEC'}")
    print("\n=== Extraits de logs ===")
    for idx, out in logs:
        print(f"--- Instance {idx+1} ---\n{out[-1000:] if out else ''}\n")

if __name__ == "__main__":
    main() 