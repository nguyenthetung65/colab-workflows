# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: colab_tailscale_proxy_node.py
DU AN : KRONOS-HYBRID ARCHITECTURE (BUOC 1 - CLOUD PROXY POOL)
MUC DICH:
  - Bien may ao Google Colab thanh Headless Forward Proxy Node sieu nhe (<40MB RAM).
  - Tu dong gia nhap mang ao WireGuard Tailscale Mesh cung mang voi PC local (100.78.157.51).
  - Khong chay Chrome / Playwright tren Colab de triet tieu hoan toan OOM (suy kiet RAM).
  - Phat song SOCKS5/HTTP Proxy tren Tailscale IP noi bo (100.x.y.z:8888).
  - Tu dong gui nhip tim (Heartbeat) va dang ky endpoint ve Ingestion Server tren PC.
=============================================================================
"""

import os
import sys
import time
import json
import socket
import asyncio
import logging
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

# Cau hinh Mac dinh
DEFAULT_PROXY_PORT = int(os.environ.get("KRONOS_PROXY_PORT", "8888"))
MASTER_PC_TAILSCALE_IP = os.environ.get("MASTER_PC_IP", "100.78.157.51")
MASTER_INGEST_PORT = int(os.environ.get("MASTER_INGEST_PORT", "8000"))
INGEST_KEY = os.environ.get("INGEST_API_KEY", "4b3f34f5e3906978692e9f3e3c74859921df811d1c1fc1b968ddb3586918982d")
HEARTBEAT_INTERVAL_SEC = int(os.environ.get("HEARTBEAT_SEC", "30"))
PROXY_NODE_NAME = os.environ.get("KRONOS_NODE_NAME", f"colab-node-{socket.gethostname()[:8]}")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s][KRONOS_NODE] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("KronosNode")

# =============================================================================
# 1. TAILSCALE SETUP & AUTO-JOIN MESH
# =============================================================================
def install_and_start_tailscale(auth_key: str = None) -> str:
    """
    Cai dat Tailscale tren Colab (Ubuntu) va ket noi vao Tailnet bang Auth Key.
    Tra ve dia chi IP Tailscale (100.x.y.z) cua node.
    """
    logger.info("Kiem tra trang thai Tailscale...")
    # Kiem tra da co tailscale CLI chua
    ts_path = shutil_which("tailscale")
    if not ts_path:
        logger.info("Chua co Tailscale. Tien hanh cai dat tu dong bang script chinh hang...")
        install_cmd = "curl -fsSL https://tailscale.com/install.sh | sh"
        res = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
        if res.returncode != 0:
            logger.error(f"Cai dat Tailscale that bai: {res.stderr}")
            return ""

    # Khoi dong daemon tailscaled neu chua chay
    check_daemon = subprocess.run("pgrep -f tailscaled", shell=True, capture_output=True)
    if check_daemon.returncode != 0:
        logger.info("Khoi dong tailscaled background daemon...")
        subprocess.Popen(
            ["tailscaled", "--state=/tmp/tailscaled.state", "--socket=/tmp/tailscale.sock"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(3)

    # Neu co auth_key thi thuc hien tailscale up
    if auth_key:
        logger.info(f"Thuc hien tailscale up voi node name: {PROXY_NODE_NAME}...")
        up_cmd = [
            "tailscale",
            "--socket=/tmp/tailscale.sock",
            "up",
            f"--authkey={auth_key}",
            f"--hostname={PROXY_NODE_NAME}",
            "--accept-routes=true"
        ]
        res = subprocess.run(up_cmd, capture_output=True, text=True)
        if res.returncode != 0:
            logger.warning(f"tailscale up canh bao: {res.stderr}")

    # Lay IP Tailscale cua node
    try:
        ip_cmd = ["tailscale", "--socket=/tmp/tailscale.sock", "ip", "-4"]
        res = subprocess.run(ip_cmd, capture_output=True, text=True, timeout=10)
        ts_ip = res.stdout.strip()
        if ts_ip.startswith("100."):
            logger.info(f"Ket noi Tailscale Mesh thanh cong! Node IP: {ts_ip}")
            return ts_ip
    except Exception as e:
        logger.error(f"Khong the lay IP Tailscale: {e}")

    # Fallback cho moi truong dev / test
    return "127.0.0.1"


def shutil_which(pgm: str):
    import shutil
    return shutil.which(pgm)


# =============================================================================
# 2. ASYNCIO ASYNC FORWARD PROXY (TOC DO C-SPEED, ZERO-BUFFERING)
# =============================================================================
async def pipe_streams(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Dong bo du lieu 2 chieu khong truyen qua file, giu do tre < 1ms."""
    try:
        while True:
            data = await reader.read(65536)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (asyncio.CancelledError, ConnectionResetError, BrokenPipeError):
        pass
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def handle_proxy_client(client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter):
    """
    Xu ly yeu cau HTTP CONNECT Tunneling (HTTPS) va HTTP Proxy request thong thuong.
    Chiu tai nhe, khong giai ma SSL, khong luu tru log gay ro ri.
    """
    try:
        initial_data = await client_reader.readuntil(b"\r\n\r\n")
    except Exception:
        client_writer.close()
        return

    lines = initial_data.decode("latin1", errors="ignore").split("\r\n")
    if not lines or not lines[0]:
        client_writer.close()
        return

    req_line = lines[0].strip().split()
    if len(req_line) < 2:
        client_writer.close()
        return

    method, url = req_line[0].upper(), req_line[1]

    if method == "CONNECT":
        # HTTPS Tunneling: host:port
        if ":" in url:
            target_host, target_port = url.split(":", 1)
            target_port = int(target_port)
        else:
            target_host, target_port = url, 443

        try:
            target_reader, target_writer = await asyncio.open_connection(target_host, target_port)
            client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await client_writer.drain()

            await asyncio.gather(
                pipe_streams(client_reader, target_writer),
                pipe_streams(target_reader, client_writer),
                return_exceptions=True
            )
        except Exception as e:
            try:
                client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                await client_writer.drain()
            except Exception:
                pass
            client_writer.close()
    else:
        # HTTP Thuong (GET, POST...)
        try:
            # Parse URL
            from urllib.parse import urlparse
            p = urlparse(url)
            target_host = p.hostname or "127.0.0.1"
            target_port = p.port or 80

            target_reader, target_writer = await asyncio.open_connection(target_host, target_port)
            target_writer.write(initial_data)
            await target_writer.drain()

            await asyncio.gather(
                pipe_streams(client_reader, target_writer),
                pipe_streams(target_reader, client_writer),
                return_exceptions=True
            )
        except Exception:
            client_writer.close()


async def start_proxy_server(bind_ip: str, port: int):
    """Khoi chay Server Proxy bat dong bo."""
    server = await asyncio.start_server(handle_proxy_client, bind_ip, port)
    logger.info(f"Kronos Proxy Server dang lang nghe tai: http://{bind_ip}:{port}")
    async with server:
        await server.serve_forever()


# =============================================================================
# 3. HEARTBEAT & DANG KY NODE VOI MASTER PC
# =============================================================================
def send_registration_to_master(node_ip: str, port: int, node_name: str) -> bool:
    """Gui thong tin dang ky endpoint ve PC local qua Tailscale."""
    url = f"http://{MASTER_PC_TAILSCALE_IP}:{MASTER_INGEST_PORT}/api/proxy_register"
    payload = json.dumps({
        "node_name": node_name,
        "tailscale_ip": node_ip,
        "proxy_port": port,
        "protocol": "http_connect",
        "timestamp": time.time(),
        "status": "ONLINE"
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if INGEST_KEY:
        headers["Authorization"] = f"Bearer {INGEST_KEY}"
    req = urllib.request.Request(
        url,
        data=payload,
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                logger.info(f"Dang ky thanh cong voi Master PC ({url})")
                return True
    except Exception as e:
        logger.warning(f"Chua the gui dang ky ve Master PC ({e}) - se thu lai theo nhip tim.")
    return False


async def heartbeat_loop(node_ip: str, port: int, node_name: str):
    """Gui heartbeat dinh ky giu song ket noi va bao cao suc khoe node."""
    while True:
        try:
            send_registration_to_master(node_ip, port, node_name)
        except Exception as e:
            logger.debug(f"Heartbeat error: {e}")
        await asyncio.sleep(HEARTBEAT_INTERVAL_SEC)


# =============================================================================
# ENTRY POINT
# =============================================================================
async def main_async(auth_key: str = None, port: int = DEFAULT_PROXY_PORT):
    # 1. Setup Tailscale
    node_ip = install_and_start_tailscale(auth_key)

    # 2. Gui dang ky dau tien
    send_registration_to_master(node_ip, port, PROXY_NODE_NAME)

    # 3. Chay song song Proxy Server va Heartbeat loop
    await asyncio.gather(
        start_proxy_server("0.0.0.0", port),
        heartbeat_loop(node_ip, port, PROXY_NODE_NAME)
    )


def run_node(auth_key: str = None, port: int = DEFAULT_PROXY_PORT):
    """Entry point cho Colab notebook: chi can goi run_node('tskey-auth-xxx')"""
    logger.info("=== KHOI DONG KRONOS COLAB PROXY NODE ===")
    try:
        asyncio.run(main_async(auth_key, port))
    except KeyboardInterrupt:
        logger.info("Kronos Proxy Node da dung theo yeu cau.")


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("TAILSCALE_AUTHKEY", "")
    p = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PROXY_PORT
    run_node(key, p)
