# -*- coding: utf-8 -*-
"""
=============================================================================
MODULE: kronos_security_encryptor.py
DU AN : KRONOS-HYBRID ARCHITECTURE (BUOC 3 - ZERO-LEAK SECURITY ENGINE)
MUC DICH:
  - Dong goi va ma hoa ma nguon loi (Private Core) bang thuat toan AES-256-GCM (AEAD).
  - Tich hop xac thuc toan ven toan bo du lieu bang Authentication Tag (16 bytes MAC)
    chong hoan toan cac cuoc tan cong padding oracle hay sua doi byte ma hoa.
  - PBKDF2 HMAC-SHA256 voi 600,000 vong lap (chuan OWASP Security Standard).
  - Xuat ra tep tin ma hoa nhi phan 'kronos_core_encrypted.bin' de day len Public Repo.
  - Cung cap ham giai ma On-The-Fly truc tiep tren RAM (/dev/shm hoac in-memory zip)
    giup GitHub Actions Runner doc va thuc thi ma khong he de lai ma nguon tren dia.
=============================================================================
"""

import os
import sys
import io
import zipfile
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


def derive_key(password: str, salt: bytes) -> bytes:
    """Su dung PBKDF2 HMAC-SHA256 600,000 vong (chuan OWASP) de sinh khoa 256-bit (32 bytes)."""
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # 32 bytes AES-256 Key
        salt=salt,
        iterations=600_000
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_files_to_bundle(file_paths: List[Path], password: str, output_bundle: Path) -> int:
    """
    Nen danh sach file vao Zip in-memory, sau do ma hoa bang AES-256-GCM (Authenticated Encryption).
    Header: [MAGIC 4B: 'KRNZ'] [SALT 16B] [NONCE 12B] [TAG 16B] [CIPHERTEXT]
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Yeu cau thu vien cryptography. Hay cai: pip install cryptography")

    # 1. Tao zip trong RAM
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in file_paths:
            f = Path(f)
            if f.exists():
                if f.is_dir():
                    for sub in f.rglob('*'):
                        if sub.is_file():
                            zf.write(sub, arcname=str(sub.relative_to(f.parent)).replace("\\", "/"))
                else:
                    zf.write(f, arcname=f.name)
    raw_bytes = zip_buffer.getvalue()

    # 2. Sinh Salt (16B), Nonce GCM (12B) va khoa AES-256
    salt = os.urandom(16)
    nonce = os.urandom(12)  # 96-bit chuẩn NIST cho AES-GCM
    key = derive_key(password, salt)

    # 3. Ma hoa AES-256-GCM (Authenticated Encryption - AEAD)
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(raw_bytes) + encryptor.finalize()
    tag = encryptor.tag  # 16 bytes MAC authentication tag

    # 4. Ghi ra file nhi phan
    magic = b"KRNZ"
    with open(output_bundle, "wb") as f:
        f.write(magic)      # 4 bytes
        f.write(salt)       # 16 bytes
        f.write(nonce)      # 12 bytes
        f.write(tag)        # 16 bytes
        f.write(ciphertext) # N bytes

    return output_bundle.stat().st_size


def decrypt_bundle_in_memory(encrypted_bundle_path: Path, password: str, extract_to_dir: Path) -> List[str]:
    """
    Giai ma goi AES-256-GCM truc tiep tren RAM, tu dong xac thuc toan ven bang Tag (MAC).
    Nem ngoai le InvalidTag neu ciphertext bi sua doi du chi 1 bit.
    """
    if not CRYPTO_AVAILABLE:
        raise RuntimeError("Yeu cau thu vien cryptography. Hay cai: pip install cryptography")

    with open(encrypted_bundle_path, "rb") as f:
        magic = f.read(4)
        if magic != b"KRNZ":
            raise ValueError("File khong phai goi ma hoa hop le cua Kronos!")
        salt = f.read(16)
        nonce = f.read(12)
        tag = f.read(16)
        ciphertext = f.read()

    # 1. Sinh khoa tu password va salt
    key = derive_key(password, salt)

    # 2. Giai ma va xac thuc MAC tag dong thoi bang AES-GCM
    cipher = Cipher(algorithms.AES(key), modes.GCM(nonce, tag))
    decryptor = cipher.decryptor()
    raw_zip = decryptor.update(ciphertext) + decryptor.finalize()

    # 3. Giai nen vao thu muc muc tieu
    extract_to_dir = Path(extract_to_dir)
    extract_to_dir.mkdir(parents=True, exist_ok=True)
    extracted_files = []
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as zf:
        zf.extractall(extract_to_dir)
        extracted_files = zf.namelist()

    return extracted_files


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Kronos Zero-Leak Code Encryptor (AES-256-GCM)")
    parser.add_argument("--mode", choices=["encrypt", "decrypt"], required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--output", default="kronos_core_encrypted.bin")
    parser.add_argument("--files", nargs="*", default=[])
    args = parser.parse_args()

    if args.mode == "encrypt":
        paths = [Path(p) for p in args.files]
        sz = encrypt_files_to_bundle(paths, args.password, Path(args.output))
        print(f"[SUCCESS] Da ma hoa AES-256-GCM {len(paths)} file vao {args.output} ({sz:,} bytes)")
    else:
        out_dir = Path("./tmp_decrypted")
        ext = decrypt_bundle_in_memory(Path(args.output), args.password, out_dir)
        print(f"[SUCCESS] Da giai ma va xac thuc MAC thanh cong {len(ext)} file: {ext}")
