import subprocess
import uuid
import os
import time
import shutil

class SoftwareSandbox:
    def __init__(self, image: str, name: str = None):
        self.image = image
        self.name = name or f"sandbox_{uuid.uuid4().hex[:8]}"
        self.report_dir = os.path.abspath(f"./reports/{self.name}")
        os.makedirs(self.report_dir, exist_ok=True)

    def start_container(self):
        subprocess.run([
            "docker", "run", "-d",
            "--name", self.name,
            "--network", "none",      # isolate network
            self.image
        ], check=True)
        print(f"[+] Container {self.name} started")

    def run_sast(self, path: str):
        """Static code scan with Semgrep"""
        report = os.path.join(self.report_dir, "sast.json")
        subprocess.run([
            "semgrep", "--config", "p/ci",  # CI ruleset
            "--json", "--output", report,
            "--exclude", "tests",
            path
        ], check=True)
        print(f"[+] SAST report: {report}")

    def run_dast(self, target: str):
        """Dynamic scan with OWASP ZAP baseline scan"""
        report = os.path.join(self.report_dir, "dast.html")
        subprocess.run([
            "zap-baseline.py",
            "-t", target,
            "-r", report,
            "-I",         # ignore breakpoints
            "-d",         # debug
        ], check=True)
        print(f"[+] DAST report: {report}")

    def cleanup(self):
        subprocess.run(["docker", "rm", "-f", self.name], check=True)
        print(f"[+] Container {self.name} removed")
        # Optionally archive or delete reports

if __name__ == "__main__":
    sb = SoftwareSandbox(image="myapp:latest")
    sb.start_container()
    time.sleep(5)  # wait for service to start
    sb.run_sast(path="./src")
    sb.run_dast(target=f"http://localhost:8080")
    sb.cleanup()
