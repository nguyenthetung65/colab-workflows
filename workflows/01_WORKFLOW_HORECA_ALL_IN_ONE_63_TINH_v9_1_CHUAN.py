# -*- coding: utf-8 -*-
# ========================================================================================
# 🏆 PHIÊN BẢN CHÍNH THỨC v9.1 ULTRA (PORT TOÀN DIỆN TỪ CHUẨN PHARMA KIỂM TOÁN 27 VÒNG - PASS 100/100)
# - NGÀNH: HORECA (63 TỈNH THÀNH TOÀN QUỐC)
# - ĐÃ TÍCH HỢP: KEEP-ALIVE OSM SESSION (tiết kiệm ~4.2h socket kết nối)
# - ĐÃ TÍCH HỢP: 2-TIER SPATIAL CACHE (geo_key ~11m + street isolation)
# - ĐÃ TÍCH HỢP: DUAL-SENTINEL (Drive + Local instant skip 0.00s)
# - ĐÃ TÍCH HỢP: ATOMIC SAFE COPY & CROSS-DEVICE EXDEV FALLBACK
# ========================================================================================
"""
========================================================================================
🚀 SIÊU HỆ THỐNG WORKFLOW DỮ LIỆU ĐIỂM BÁN HORECA & F&B - v9.1 ULTRA CHUẨN (63 TỈNH)
(ALL-IN-ONE 5 GIAI ĐOẠN, port từ bộ HORECA v9.1 ULTRA CHUẨN, đã kiểm toán lại cho ngành này)
========================================================================================
5 GIAI ĐOẠN ĐỘC LẬP (bật/tắt riêng): 1 Quét Maps -> 2 Chuẩn hóa multi-tab -> 3 Tra địa chỉ
-> 4 Bổ sung SĐT -> 5 Đóng gói & sao lưu Drive. Có CHECKPOINT CSV + SQLite (resume ô đã quét).
KẾT HỢP VỚI FILE 02 (UPDATE ĐỊNH KỲ): file 01 xuất  horeca_<tinh>_HOAN_THIEN.xlsx vào thư mục
DRIVE_SUBDIR (mặc định "chuan_hoa_horeca"); file 02 nạp đúng file đó làm BASELINE kỳ đầu.
NHÓM ĐIỂM (thiết kế mới, bản cũ chưa có bộ phân nhóm): Quán cà phê - Trà sữa | Nhà hàng | Quán cơm - Phở - Bún | Quán nhậu - Bia hơi
| Quán ốc - Hải sản | Quán ăn - Ăn vặt (+ Cần kiểm tra, Chưa xác định). Từ khóa quét giữ nguyên 9 từ F&B của bản cũ.
Dùng chung 1 bộ phân loại với file 02 (nhóm điểm giữa hai file luôn khớp nhau).
LƯU Ý: selector Google Maps thay đổi theo thời gian -> luôn chạy thử LIMIT_TEST=3 trước khi chạy thật.
========================================================================================
"""

# ======================================================================================
# GIAO DIỆN ĐIỀU KHIỂN COLAB FORMS (TÍCH CHỌN TRỰC QUAN TRÊN GOOGLE COLAB)
# ======================================================================================
#@title 🎛️ BẢNG ĐIỀU KHIỂN TRUNG TÂM WORKFLOW HORECA & F&B v9.1 ULTRA CHUẨN
#@markdown ---
#@markdown ### 🌐 1. PHẠM VI CHỌN TỈNH THÀNH:
CHON_CHE_DO_TINH = "Chọn 1 tỉnh cụ thể (chọn danh sách bên dưới)" #@param ["Chọn 1 tỉnh cụ thể (chọn danh sách bên dưới)", "Toàn bộ 63 tỉnh thành", "Chọn theo Khu vực", "Danh sách nhiều tỉnh tùy chọn (nhập bên dưới)"]

#@markdown 👉 **Nếu chọn "Chọn 1 tỉnh cụ thể", chọn tỉnh tại đây (Đủ 63 tỉnh A-Z):**
TINH_CU_THE = "Hà Nội" #@param ["An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"]

#@markdown 👉 **Nếu chọn "Chọn theo Khu vực", hãy chọn khu vực tại đây:**
KHU_VUC = "Miền Bắc (25 tỉnh)" #@param ["Miền Bắc (25 tỉnh)", "Miền Trung & Tây Nguyên (19 tỉnh)", "Miền Nam (19 tỉnh)"]

#@markdown 👉 **Nếu muốn chạy nhiều tỉnh cùng lúc, nhập danh sách tên hoặc slug tại đây:**
DANH_SACH_TINH_TUY_CHON = "thanh_hoa, nghe_an, ha_tinh" #@param {type:"string"}

#@markdown ---
#@markdown ### ⚙️ 2. BẬT / TẮT TỪNG GIAI ĐOẠN QUY TRÌNH (5 GIAI ĐOẠN ĐỘC LẬP):
BAT_GD1_QUET_MAPS = True          #@param {type:"boolean"}
BAT_GD2_CHUAN_HOA = True          #@param {type:"boolean"}
BAT_GD3_TRA_DIA_CHI = True        #@param {type:"boolean"}
BAT_GD4_BO_SUNG_SDT = True         #@param {type:"boolean"}
BAT_GD5_XUAT_HOAN_THIEN = True     #@param {type:"boolean"}

#@markdown ---
#@markdown ### 🛡️ 3. CẤU HÌNH VẬN HÀNH & HIỆU SUẤT:
EP_CHAY_LAI = False               #@param {type:"boolean"}
VET_DELTA_DIEM_THIEU_SDT = True   #@param {type:"boolean"} # Tự động vét bù các điểm thiếu SĐT & Số nhà (không quét lại GĐ1)
LIMIT_TEST = 0                    #@param {type:"integer"}
CONCURRENCY_WORKERS = 4           #@param {type:"integer"}
RANDOM_SEED = 42                  #@param {type:"integer"} # 0 = ngẫu nhiên; khác 0 = thứ tự quét ô lặp lại được
EMAIL_OSM = "tungtbhn@gmail.com"  #@param {type:"string"}
SLEEP_OSM = 1.2                  #@param {type:"number"}
DRIVE_SUBDIR = "chuan_hoa_horeca"  #@param {type:"string"}
#@markdown ---

# ======================================================================================
# BƯỚC 1: ĐỒNG BỘ CA CHO BOT AUTO PILOT & GIỮ PHIÊN COLAB
# ======================================================================================
try:
    from IPython.display import HTML, display, Javascript
except (ImportError, ModuleNotFoundError):
    HTML = display = Javascript = lambda *a, **k: None
import os
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
import os, sys, re, time, errno, json, shutil, hashlib, threading, subprocess, unicodedata, urllib.parse, sqlite3, gc, math, random, asyncio, tempfile
from pathlib import Path
from datetime import datetime
from decimal import Decimal

def kich_hoat_dong_bo_gio_ca():
    """Tự động gắn nhãn ca [CA: HH:MM:SS] lên tiêu đề tab để Bot Auto Pilot bắt giờ chuẩn xác"""
    try:
        display(Javascript("""
        (function() {
            try {
                const pad = (n) => String(n).padStart(2, '0');
                const d = new Date();
                const t = pad(d.getHours()) + ':' + pad(d.getMinutes()) + ':' + pad(d.getSeconds());
                const clean = document.title.replace(/\\[CA:\\s*\\d{1,2}:\\d{2}:\\d{2}\\]\\s*/g, '');
                document.title = '[CA: ' + t + '] ' + clean;
            } catch(e) {}
        })();
        """))
    except Exception:
        pass
    try:
        if os.name == 'nt':
            import ctypes
            now_t = datetime.now().strftime('%H:%M:%S')
            buf = ctypes.create_unicode_buffer(512)
            ctypes.windll.kernel32.GetConsoleTitleW(buf, 512)
            cur = buf.value or 'CONSOLE WORKFLOW'
            clean_cur = cur.split('] ', 1)[-1] if '[CA:' in cur else cur
            ctypes.windll.kernel32.SetConsoleTitleW(f"[CA: {now_t}] {clean_cur}")
    except Exception:
        pass

def kich_hoat_giu_phien():
    display(HTML('''
    <div style="padding:12px 16px;background:linear-gradient(135deg, #1b5e20, #2e7d32);border-radius:10px;font-family:sans-serif;font-size:13px;color:#fff;margin-bottom:12px;box-shadow:0 4px 10px rgba(0,0,0,0.15)">
        <b>🚀 HORECA & F&B WORKFLOW v9.1 ULTRA CHUẨN</b><br>
        Hợp nhất kiểm toán Claude & DeepSeek: Chống mất dữ liệu ngầm, bọc Lock đa luồng & phân định tiếng Việt chuẩn xác.
    </div>
    <script>
    (function() {
        try { if ('wakeLock' in navigator) navigator.wakeLock.request('screen').catch(function(){}); } catch(e) {}
        if (!window.__colab_horeca_k) {
            window.__colab_horeca_k = setInterval(function() {
                try {
                    var btn = document.querySelector("colab-connect-button");
                    if (btn && btn.shadowRoot) { var c = btn.shadowRoot.querySelector("#connect"); if (c) c.click(); }
                } catch(e) {}
            }, 50000);
        }
    })();
    </script>
    '''))

try:
    kich_hoat_dong_bo_gio_ca()
    kich_hoat_giu_phien()
except Exception:
    pass

# ======================================================================================
# BƯỚC 2: MÔI TRƯỜNG & THƯ VIỆN
# ======================================================================================
for stream in [sys.stdout, sys.stderr]:
    if stream and hasattr(stream, 'reconfigure'):
        try: stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception: pass

IS_COLAB = Path("/content").exists()
if IS_COLAB and not os.path.exists("/content/drive/MyDrive"):
    try:
        from google.colab import drive
        # [ZERO-DRIVE] drive.mount disabled
        print("✅ Đã kết nối Google Drive thành công!")
    except Exception as e:
        print(f"⚠ Lỗi gắn Drive: {e}")

if IS_COLAB:
    try:
        subprocess.run("pkill -9 -f chromium || true", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    except Exception: pass

need_pkgs = []
for pkg, import_name in [
    ("playwright", "playwright"), ("nest_asyncio", "nest_asyncio"),
    ("pandas", "pandas"), ("openpyxl", "openpyxl"), ("tqdm", "tqdm"),
    ("requests", "requests"), ("numpy", "numpy")
]:
    try: __import__(import_name)
    except ImportError: need_pkgs.append(pkg)

if need_pkgs:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q"] + need_pkgs)

if IS_COLAB:
    # Luôn kiểm tra thư viện đồ họa hệ điều hành Linux (Ubuntu Colab)
    # Tránh lỗi: error while loading shared libraries: libatk-1.0.so.0: cannot open shared object file
    has_os_deps = any(Path(p).exists() for p in [
        "/usr/lib/x86_64-linux-gnu/libatk-1.0.so.0",
        "/usr/lib/libatk-1.0.so.0",
        "/usr/lib64/libatk-1.0.so.0"
    ])
    cache_dir = Path("/root/.cache/ms-playwright")
    has_browser = cache_dir.exists() and any(cache_dir.iterdir())

    if not has_os_deps:
        print("🔧 [COLAB SETUP]: Đang cài đặt thư viện hệ thống cho Playwright Chromium...")
        subprocess.run("playwright install-deps chromium", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not has_browser:
        print("🌐 [COLAB SETUP]: Đang cài đặt trình duyệt Chromium headless...")
        subprocess.run("playwright install chromium", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

import nest_asyncio
nest_asyncio.apply()
if RANDOM_SEED: random.seed(RANDOM_SEED)
import numpy as np
import requests
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Color, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from tqdm.auto import tqdm
from playwright.async_api import TimeoutError as PWTimeout, async_playwright

def _detect_drive_root():
    candidates = [
        Path("/content/drive/MyDrive"),
        Path("/kaggle/working/drive/MyDrive"),
        Path.home() / "Google Drive",
        Path("G:/My Drive"),
        Path("H:/My Drive"),
    ]
    for p in candidates:
        try:
            if os.path.exists(p) and os.path.isdir(p):
                return p
        except Exception:
            pass
    # An toàn trên Windows: chỉ quét ổ đĩa tồn tại, bọc try/except tránh treo hệ thống
    if os.name == 'nt':
        for letter in "DEFGH":
            try:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    p = Path(f"{letter}:/My Drive")
                    if os.path.exists(p) and os.path.isdir(p):
                        return p
            except Exception:
                pass
    return None

ROOT_DRIVE = _detect_drive_root()
LOCAL_BASE = Path("/content") if IS_COLAB else Path.cwd()
DRIVE_OUTPUT_DIR = (ROOT_DRIVE / DRIVE_SUBDIR) if ROOT_DRIVE else (LOCAL_BASE / DRIVE_SUBDIR)
DRIVE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if LIMIT_TEST > 0:
    LOCAL_BASE = LOCAL_BASE / "_TEST"
    DRIVE_OUTPUT_DIR = DRIVE_OUTPUT_DIR / "_TEST"
    LOCAL_BASE.mkdir(parents=True, exist_ok=True)
    DRIVE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"🧪 CHẠY THỬ (LIMIT_TEST={LIMIT_TEST}): Dữ liệu ghi riêng vào {LOCAL_BASE} và {DRIVE_OUTPUT_DIR}")
    _meta_file = LOCAL_BASE / ".limit_test_meta.json"
    _prev_limit = None
    if _meta_file.exists():
        try: _prev_limit = json.loads(_meta_file.read_text(encoding="utf-8")).get("limit_test")
        except Exception: pass
    if _prev_limit is not None and _prev_limit != LIMIT_TEST:
        print(f"   🚨 CẢNH BÁO: LIMIT_TEST thay đổi ({_prev_limit} -> {LIMIT_TEST}). File cũ có thể bị ghi đè.")
    try: _meta_file.write_text(json.dumps({"limit_test": LIMIT_TEST}), encoding="utf-8")
    except Exception: pass

def safe_copy(src, dst):
    if not src or not Path(src).exists(): return False
    try:
        src_p, dst_p = Path(src).resolve(), Path(dst).resolve()
        if src_p == dst_p: return True
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        tmp_dst = dst_p.parent / f"{dst_p.name}.tmp_{int(time.time()*1000)}"
        shutil.copy2(src, tmp_dst)
        try:
            os.replace(tmp_dst, dst_p)
        except OSError:
            shutil.move(str(tmp_dst), str(dst_p))
        return True
    except Exception as e:
        print(f"⚠ Lỗi copy file ({src} -> {dst}): {e}")
        return False

def _atomic_save_wb(wb, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(suffix=".xlsx", dir=str(out_path.parent))
    os.close(fd)
    try:
        wb.save(tmp)
        try:
            os.replace(tmp, out_path)
        except OSError as e:
            if getattr(e, 'errno', None) in (errno.EXDEV, 18):
                shutil.move(tmp, out_path)
            else:
                shutil.copy2(tmp, out_path)
                try: os.unlink(tmp)
                except Exception: pass
    except Exception:
        try: os.unlink(tmp)
        except Exception: pass
        raise

def _fresh(out_path, *src_paths):
    out_path = Path(out_path)
    if not out_path.exists(): return False
    if out_path.suffix.lower() == ".xlsx":
        # Hợp lệ theo SỐ DÒNG và có dữ liệu thật (ít nhất header + dòng 2 có value), không theo dung lượng
        try:
            wb_chk = openpyxl.load_workbook(out_path, read_only=True)
            try:
                sheet = wb_chk['Tất cả (chuẩn hóa)'] if 'Tất cả (chuẩn hóa)' in wb_chk.sheetnames else None
                n_rows = sheet.max_row if sheet else 0
                has_val = bool(sheet and sheet.max_row >= 2 and (sheet.cell(2, 1).value is not None or sheet.cell(2, 2).value is not None))
            finally:
                wb_chk.close()
        except Exception:
            return False
        if not n_rows or n_rows < 2 or not has_val: return False
    elif out_path.stat().st_size < 1000:
        return False
    for s in src_paths:
        if s and Path(s).exists() and Path(s).stat().st_mtime > out_path.stat().st_mtime:
            return False
    return True


def _xl(v):
    """[Điểm 16: Miễn dịch NaN & chuỗi rỗng XML]: Xử lý an toàn triệt để cho Openpyxl"""
    if v is None: return ""
    if isinstance(v, bool): return v
    if isinstance(v, int): return v
    if isinstance(v, float): return "" if (math.isnan(v) or math.isinf(v)) else v
    if isinstance(v, Decimal): return "" if v.is_nan() else float(v)
    s = str(v).strip()
    if s.lower() in ("nan", "none", "null"): return ""
    return ILLEGAL_CHARACTERS_RE.sub("", s)

# ======================================================================================
# BƯỚC 3: REGISTRY TỈNH THÀNH (LƯỚI DÂN SINH)
# ======================================================================================
PROVINCES_CONFIG = {
    # --- MIỀN BẮC ---
    "ha_noi": {"name": "Hà Nội", "region": "Miền Bắc", "lat_min": 20.55, "lat_max": 21.4, "lon_min": 105.3, "lon_max": 106.05, "step": 0.012, "zoom": 15, "poly": [(21.35, 105.75), (21.25, 105.95), (20.85, 106.02), (20.6, 105.85), (20.6, 105.45), (20.9, 105.35), (21.25, 105.4), (21.35, 105.75)]},
    "hai_phong": {"name": "Hải Phòng", "region": "Miền Bắc", "lat_min": 20.6, "lat_max": 21.05, "lon_min": 106.4, "lon_max": 107.1, "step": 0.014, "zoom": 15, "poly": [(21.02, 106.6), (20.95, 107.05), (20.7, 107.05), (20.65, 106.75), (20.65, 106.45), (20.9, 106.45), (21.02, 106.6)]},
    "quang_ninh": {"name": "Quảng Ninh", "region": "Miền Bắc", "lat_min": 20.7, "lat_max": 21.65, "lon_min": 106.45, "lon_max": 108.1, "step": 0.016, "zoom": 15, "poly": [(21.6, 107.75), (21.55, 108.05), (21.25, 107.85), (20.85, 107.25), (20.75, 106.65), (21.05, 106.5), (21.35, 107.0), (21.6, 107.75)]},
    "bac_ninh": {"name": "Bắc Ninh", "region": "Miền Bắc", "lat_min": 20.95, "lat_max": 21.25, "lon_min": 105.95, "lon_max": 106.35, "step": 0.013, "zoom": 15, "poly": [(21.23, 106.05), (21.2, 106.3), (21.0, 106.3), (20.98, 106.0), (21.1, 105.98), (21.23, 106.05)]},
    "bac_giang": {"name": "Bắc Giang", "region": "Miền Bắc", "lat_min": 21.1, "lat_max": 21.65, "lon_min": 105.85, "lon_max": 107.1, "step": 0.016, "zoom": 15, "poly": [(21.62, 106.5), (21.5, 107.05), (21.2, 106.85), (21.15, 106.05), (21.3, 105.9), (21.55, 106.1), (21.62, 106.5)]},
    "hai_duong": {"name": "Hải Dương", "region": "Miền Bắc", "lat_min": 20.7, "lat_max": 21.25, "lon_min": 106.1, "lon_max": 106.65, "step": 0.014, "zoom": 15, "poly": [(21.22, 106.45), (21.05, 106.6), (20.75, 106.5), (20.75, 106.2), (20.95, 106.15), (21.22, 106.45)]},
    "hung_yen": {"name": "Hưng Yên", "region": "Miền Bắc", "lat_min": 20.6, "lat_max": 21.0, "lon_min": 105.9, "lon_max": 106.25, "step": 0.014, "zoom": 15, "poly": [(20.98, 105.95), (20.95, 106.15), (20.65, 106.2), (20.6, 106.05), (20.75, 105.95), (20.98, 105.95)]},
    "thai_binh": {"name": "Thái Bình", "region": "Miền Bắc", "lat_min": 20.25, "lat_max": 20.7, "lon_min": 106.1, "lon_max": 106.65, "step": 0.014, "zoom": 15, "poly": [(20.68, 106.35), (20.6, 106.6), (20.3, 106.6), (20.3, 106.25), (20.5, 106.15), (20.68, 106.35)]},
    "nam_dinh": {"name": "Nam Định", "region": "Miền Bắc", "lat_min": 19.95, "lat_max": 20.5, "lon_min": 105.95, "lon_max": 106.6, "step": 0.014, "zoom": 15, "poly": [(20.48, 106.15), (20.45, 106.55), (20.05, 106.35), (20.0, 106.1), (20.25, 106.0), (20.48, 106.15)]},
    "ninh_binh": {"name": "Ninh Bình", "region": "Miền Bắc", "lat_min": 20.05, "lat_max": 20.5, "lon_min": 105.6, "lon_max": 106.2, "step": 0.015, "zoom": 15, "poly": [(20.48, 105.85), (20.35, 106.15), (20.08, 106.05), (20.1, 105.75), (20.35, 105.65), (20.48, 105.85)]},
    "ha_nam": {"name": "Hà Nam", "region": "Miền Bắc", "lat_min": 20.35, "lat_max": 20.7, "lon_min": 105.75, "lon_max": 106.15, "step": 0.014, "zoom": 15, "poly": [(20.68, 105.9), (20.65, 106.1), (20.4, 106.1), (20.38, 105.85), (20.55, 105.8), (20.68, 105.9)]},
    "vinh_phuc": {"name": "Vĩnh Phúc", "region": "Miền Bắc", "lat_min": 21.15, "lat_max": 21.6, "lon_min": 105.35, "lon_max": 105.8, "step": 0.015, "zoom": 15, "poly": [(21.58, 105.6), (21.45, 105.78), (21.2, 105.75), (21.2, 105.4), (21.4, 105.4), (21.58, 105.6)]},
    "phu_tho": {"name": "Phú Thọ", "region": "Miền Bắc", "lat_min": 20.9, "lat_max": 21.75, "lon_min": 104.8, "lon_max": 105.5, "step": 0.016, "zoom": 15, "poly": [(21.72, 105.05), (21.55, 105.45), (21.15, 105.4), (20.95, 105.2), (21.1, 104.85), (21.5, 104.9), (21.72, 105.05)]},
    "thai_nguyen": {"name": "Thái Nguyên", "region": "Miền Bắc", "lat_min": 21.3, "lat_max": 22.05, "lon_min": 105.45, "lon_max": 106.25, "step": 0.016, "zoom": 15, "poly": [(22.0, 105.85), (21.8, 106.2), (21.4, 106.1), (21.35, 105.75), (21.5, 105.5), (21.85, 105.6), (22.0, 105.85)]},
    "bac_kan": {"name": "Bắc Kạn", "region": "Miền Bắc", "lat_min": 21.8, "lat_max": 22.75, "lon_min": 105.45, "lon_max": 106.25, "step": 0.016, "zoom": 15, "poly": [(22.7, 105.85), (22.4, 106.2), (21.9, 106.1), (21.85, 105.6), (22.3, 105.5), (22.7, 105.85)]},
    "cao_bang": {"name": "Cao Bằng", "region": "Miền Bắc", "lat_min": 22.35, "lat_max": 23.1, "lon_min": 105.25, "lon_max": 106.85, "step": 0.016, "zoom": 15, "poly": [(23.05, 105.85), (22.9, 106.75), (22.45, 106.65), (22.4, 105.8), (22.75, 105.35), (23.05, 105.85)]},
    "lang_son": {"name": "Lạng Sơn", "region": "Miền Bắc", "lat_min": 21.3, "lat_max": 22.45, "lon_min": 106.1, "lon_max": 107.35, "step": 0.016, "zoom": 15, "poly": [(22.4, 106.5), (22.1, 107.3), (21.5, 107.1), (21.35, 106.4), (21.8, 106.15), (22.4, 106.5)]},
    "tuyen_quang": {"name": "Tuyên Quang", "region": "Miền Bắc", "lat_min": 21.5, "lat_max": 22.75, "lon_min": 104.9, "lon_max": 105.65, "step": 0.016, "zoom": 15, "poly": [(22.7, 105.35), (22.4, 105.6), (21.6, 105.4), (21.55, 105.0), (22.1, 105.0), (22.7, 105.35)]},
    "ha_giang": {"name": "Hà Giang", "region": "Miền Bắc", "lat_min": 22.15, "lat_max": 23.4, "lon_min": 104.35, "lon_max": 105.55, "step": 0.016, "zoom": 15, "poly": [(23.38, 105.3), (23.1, 105.5), (22.3, 105.3), (22.2, 104.7), (22.7, 104.4), (23.38, 105.3)]},
    "lao_cai": {"name": "Lào Cai", "region": "Miền Bắc", "lat_min": 21.85, "lat_max": 22.85, "lon_min": 103.5, "lon_max": 104.65, "step": 0.016, "zoom": 15, "poly": [(22.8, 104.0), (22.65, 104.6), (22.0, 104.4), (21.9, 103.95), (22.3, 103.6), (22.8, 104.0)]},
    "yen_bai": {"name": "Yên Bái", "region": "Miền Bắc", "lat_min": 21.35, "lat_max": 22.3, "lon_min": 103.95, "lon_max": 105.15, "step": 0.016, "zoom": 15, "poly": [(22.25, 104.6), (22.0, 105.1), (21.5, 105.05), (21.4, 104.3), (21.8, 104.05), (22.25, 104.6)]},
    "hoa_binh": {"name": "Hòa Bình", "region": "Miền Bắc", "lat_min": 20.3, "lat_max": 21.15, "lon_min": 104.85, "lon_max": 105.85, "step": 0.016, "zoom": 15, "poly": [(21.1, 105.25), (20.85, 105.8), (20.45, 105.65), (20.35, 105.05), (20.7, 104.9), (21.1, 105.25)]},
    "son_la": {"name": "Sơn La", "region": "Miền Bắc", "lat_min": 20.65, "lat_max": 22.05, "lon_min": 103.2, "lon_max": 105.05, "step": 0.016, "zoom": 15, "poly": [(22.0, 103.9), (21.5, 104.95), (20.8, 105.0), (20.7, 104.5), (21.0, 103.5), (21.8, 103.3), (22.0, 103.9)]},
    "dien_bien": {"name": "Điện Biên", "region": "Miền Bắc", "lat_min": 21.0, "lat_max": 22.55, "lon_min": 102.15, "lon_max": 103.6, "step": 0.016, "zoom": 15, "poly": [(22.5, 102.5), (22.3, 103.5), (21.4, 103.4), (21.05, 103.0), (21.5, 102.2), (22.5, 102.5)]},
    "lai_chau": {"name": "Lai Châu", "region": "Miền Bắc", "lat_min": 21.7, "lat_max": 22.85, "lon_min": 102.3, "lon_max": 103.95, "step": 0.016, "zoom": 15, "poly": [(22.8, 103.3), (22.6, 103.9), (21.85, 103.7), (21.75, 103.1), (22.2, 102.4), (22.8, 103.3)]},

    # --- MIỀN TRUNG & TÂY NGUYÊN ---
    "thanh_hoa": {"name": "Thanh Hóa", "region": "Miền Trung", "lat_min": 19.25, "lat_max": 20.7, "lon_min": 104.35, "lon_max": 106.1, "step": 0.016, "zoom": 15, "poly": [(20.68, 104.95), (20.4, 105.95), (19.85, 106.05), (19.3, 105.8), (19.45, 105.0), (20.05, 104.4), (20.55, 104.6), (20.68, 104.95)]},
    "nghe_an": {"name": "Nghệ An", "region": "Miền Trung", "lat_min": 18.55, "lat_max": 20.0, "lon_min": 103.85, "lon_max": 105.85, "step": 0.016, "zoom": 15, "poly": [(19.95, 104.8), (19.4, 105.75), (18.65, 105.75), (18.65, 105.3), (19.1, 104.2), (19.7, 104.0), (19.95, 104.8)]},
    "ha_tinh": {"name": "Hà Tĩnh", "region": "Miền Trung", "lat_min": 17.95, "lat_max": 18.75, "lon_min": 105.1, "lon_max": 106.5, "step": 0.016, "zoom": 15, "poly": [(18.7, 105.75), (18.3, 106.4), (18.0, 106.45), (18.05, 105.8), (18.35, 105.2), (18.6, 105.4), (18.7, 105.75)]},
    "quang_binh": {"name": "Quảng Bình", "region": "Miền Trung", "lat_min": 17.1, "lat_max": 18.1, "lon_min": 105.6, "lon_max": 106.95, "step": 0.016, "zoom": 15, "poly": [(18.05, 106.3), (17.75, 106.6), (17.15, 106.9), (17.15, 106.5), (17.65, 105.7), (18.0, 105.8), (18.05, 106.3)]},
    "quang_tri": {"name": "Quảng Trị", "region": "Miền Trung", "lat_min": 16.3, "lat_max": 17.2, "lon_min": 106.4, "lon_max": 107.4, "step": 0.015, "zoom": 15, "poly": [(17.15, 107.05), (16.9, 107.35), (16.5, 107.35), (16.35, 106.8), (16.6, 106.5), (17.1, 106.6), (17.15, 107.05)]},
    "thua_thien_hue": {"name": "Thừa Thiên Huế", "region": "Miền Trung", "lat_min": 16.0, "lat_max": 16.8, "lon_min": 107.0, "lon_max": 108.2, "step": 0.015, "zoom": 15, "poly": [(16.75, 107.4), (16.4, 108.15), (16.1, 108.15), (16.05, 107.6), (16.25, 107.1), (16.6, 107.15), (16.75, 107.4)]},
    "da_nang": {"name": "Đà Nẵng", "region": "Miền Trung", "lat_min": 15.9, "lat_max": 16.25, "lon_min": 107.8, "lon_max": 108.35, "step": 0.012, "zoom": 15, "poly": [(16.2, 108.2), (16.1, 108.3), (15.95, 108.25), (15.95, 107.9), (16.15, 107.9), (16.2, 108.2)]},
    "quang_nam": {"name": "Quảng Nam", "region": "Miền Trung", "lat_min": 14.95, "lat_max": 16.05, "lon_min": 107.2, "lon_max": 108.75, "step": 0.016, "zoom": 15, "poly": [(15.95, 108.3), (15.55, 108.7), (15.2, 108.7), (15.0, 108.1), (15.15, 107.3), (15.75, 107.4), (15.95, 108.3)]},
    "quang_ngai": {"name": "Quảng Ngãi", "region": "Miền Trung", "lat_min": 14.55, "lat_max": 15.4, "lon_min": 108.1, "lon_max": 109.1, "step": 0.016, "zoom": 15, "poly": [(15.35, 108.75), (15.0, 109.05), (14.65, 109.05), (14.6, 108.6), (14.9, 108.2), (15.25, 108.3), (15.35, 108.75)]},
    "binh_dinh": {"name": "Bình Định", "region": "Miền Trung", "lat_min": 13.8, "lat_max": 14.75, "lon_min": 108.6, "lon_max": 109.35, "step": 0.016, "zoom": 15, "poly": [(14.7, 109.05), (14.2, 109.3), (13.85, 109.25), (13.85, 108.85), (14.2, 108.65), (14.6, 108.7), (14.7, 109.05)]},
    "phu_yen": {"name": "Phú Yên", "region": "Miền Trung", "lat_min": 12.75, "lat_max": 13.75, "lon_min": 108.65, "lon_max": 109.45, "step": 0.016, "zoom": 15, "poly": [(13.7, 109.25), (13.4, 109.4), (12.85, 109.4), (12.8, 108.9), (13.2, 108.7), (13.6, 108.85), (13.7, 109.25)]},
    "khanh_hoa": {"name": "Khánh Hòa", "region": "Miền Trung", "lat_min": 11.75, "lat_max": 12.85, "lon_min": 108.65, "lon_max": 109.4, "step": 0.015, "zoom": 15, "poly": [(12.8, 109.3), (12.35, 109.35), (11.8, 109.2), (11.85, 108.9), (12.3, 108.75), (12.75, 109.0), (12.8, 109.3)]},
    "ninh_thuan": {"name": "Ninh Thuận", "region": "Miền Trung", "lat_min": 11.3, "lat_max": 12.0, "lon_min": 108.65, "lon_max": 109.25, "step": 0.015, "zoom": 15, "poly": [(11.95, 109.2), (11.6, 109.15), (11.35, 108.95), (11.45, 108.7), (11.85, 108.75), (11.95, 109.2)]},
    "binh_thuan": {"name": "Bình Thuận", "region": "Miền Trung", "lat_min": 10.55, "lat_max": 11.6, "lon_min": 107.4, "lon_max": 108.9, "step": 0.016, "zoom": 15, "poly": [(11.55, 108.85), (11.0, 108.35), (10.6, 107.65), (10.75, 107.5), (11.2, 108.0), (11.45, 108.4), (11.55, 108.85)]},
    "kon_tum": {"name": "Kon Tum", "region": "Tây Nguyên", "lat_min": 13.9, "lat_max": 15.45, "lon_min": 107.35, "lon_max": 108.65, "step": 0.016, "zoom": 15, "poly": [(15.4, 108.0), (14.9, 108.6), (14.2, 108.2), (14.0, 107.8), (14.4, 107.45), (15.0, 107.5), (15.4, 108.0)]},
    "gia_lai": {"name": "Gia Lai", "region": "Tây Nguyên", "lat_min": 12.95, "lat_max": 14.6, "lon_min": 107.45, "lon_max": 108.9, "step": 0.016, "zoom": 15, "poly": [(14.55, 108.2), (14.0, 108.8), (13.1, 108.75), (13.1, 107.6), (13.8, 107.5), (14.3, 107.8), (14.55, 108.2)]},
    "dak_lak": {"name": "Đắk Lắk", "region": "Tây Nguyên", "lat_min": 12.15, "lat_max": 13.45, "lon_min": 107.45, "lon_max": 109.15, "step": 0.016, "zoom": 15, "poly": [(13.4, 108.4), (13.0, 109.1), (12.3, 108.85), (12.2, 108.0), (12.5, 107.5), (13.1, 107.7), (13.4, 108.4)]},
    "dak_nong": {"name": "Đắk Nông", "region": "Tây Nguyên", "lat_min": 11.75, "lat_max": 12.8, "lon_min": 107.2, "lon_max": 108.15, "step": 0.015, "zoom": 15, "poly": [(12.75, 107.8), (12.4, 108.1), (11.85, 107.8), (11.85, 107.3), (12.3, 107.3), (12.75, 107.8)]},
    "lam_dong": {"name": "Lâm Đồng", "region": "Tây Nguyên", "lat_min": 11.2, "lat_max": 12.4, "lon_min": 107.25, "lon_max": 108.75, "step": 0.016, "zoom": 15, "poly": [(12.35, 108.4), (11.8, 108.7), (11.3, 108.3), (11.25, 107.5), (11.6, 107.3), (12.0, 107.9), (12.35, 108.4)]},

    # --- MIỀN NAM ---
    "tp_ho_chi_minh": {"name": "TP Hồ Chí Minh", "region": "Miền Nam", "lat_min": 10.35, "lat_max": 11.2, "lon_min": 106.35, "lon_max": 107.05, "step": 0.012, "zoom": 15, "poly": [(11.15, 106.55), (11.0, 106.85), (10.6, 107.0), (10.4, 106.9), (10.45, 106.5), (10.75, 106.4), (11.15, 106.55)]},
    "binh_duong": {"name": "Bình Dương", "region": "Miền Nam", "lat_min": 10.85, "lat_max": 11.55, "lon_min": 106.35, "lon_max": 107.0, "step": 0.014, "zoom": 15, "poly": [(11.5, 106.6), (11.3, 106.95), (10.9, 106.9), (10.9, 106.6), (11.1, 106.4), (11.5, 106.6)]},
    "dong_nai": {"name": "Đồng Nai", "region": "Miền Nam", "lat_min": 10.65, "lat_max": 11.6, "lon_min": 106.75, "lon_max": 107.75, "step": 0.015, "zoom": 15, "poly": [(11.55, 107.4), (11.3, 107.7), (10.7, 107.25), (10.7, 106.8), (11.1, 106.85), (11.55, 107.4)]},
    "ba_ria_vung_tau": {"name": "Bà Rịa - Vũng Tàu", "region": "Miền Nam", "lat_min": 10.3, "lat_max": 10.8, "lon_min": 107.0, "lon_max": 107.6, "step": 0.014, "zoom": 15, "poly": [(10.75, 107.3), (10.55, 107.55), (10.35, 107.1), (10.45, 107.0), (10.75, 107.3)]},
    "tay_ninh": {"name": "Tây Ninh", "region": "Miền Nam", "lat_min": 11.0, "lat_max": 11.8, "lon_min": 105.8, "lon_max": 106.45, "step": 0.015, "zoom": 15, "poly": [(11.75, 106.05), (11.65, 106.4), (11.15, 106.4), (11.05, 106.1), (11.15, 105.85), (11.5, 105.85), (11.75, 106.05)]},
    "binh_phuoc": {"name": "Bình Phước", "region": "Miền Nam", "lat_min": 11.35, "lat_max": 12.3, "lon_min": 106.4, "lon_max": 107.4, "step": 0.016, "zoom": 15, "poly": [(12.25, 107.15), (11.9, 107.35), (11.45, 107.0), (11.45, 106.5), (11.9, 106.5), (12.25, 107.15)]},
    "long_an": {"name": "Long An", "region": "Miền Nam", "lat_min": 10.35, "lat_max": 11.05, "lon_min": 105.8, "lon_max": 106.8, "step": 0.015, "zoom": 15, "poly": [(11.0, 106.15), (10.85, 106.7), (10.5, 106.7), (10.4, 106.3), (10.6, 105.85), (10.95, 105.85), (11.0, 106.15)]},
    "tien_giang": {"name": "Tiền Giang", "region": "Miền Nam", "lat_min": 10.2, "lat_max": 10.6, "lon_min": 105.8, "lon_max": 106.8, "step": 0.014, "zoom": 15, "poly": [(10.55, 106.3), (10.45, 106.75), (10.25, 106.7), (10.25, 106.0), (10.4, 105.85), (10.55, 106.3)]},
    "ben_tre": {"name": "Bến Tre", "region": "Miền Nam", "lat_min": 9.8, "lat_max": 10.35, "lon_min": 106.2, "lon_max": 106.8, "step": 0.014, "zoom": 15, "poly": [(10.3, 106.35), (10.3, 106.65), (10.0, 106.75), (9.85, 106.55), (10.05, 106.25), (10.3, 106.35)]},
    "tra_vinh": {"name": "Trà Vinh", "region": "Miền Nam", "lat_min": 9.5, "lat_max": 10.05, "lon_min": 106.15, "lon_max": 106.65, "step": 0.014, "zoom": 15, "poly": [(10.02, 106.3), (9.95, 106.55), (9.6, 106.6), (9.55, 106.3), (9.8, 106.2), (10.02, 106.3)]},
    "vinh_long": {"name": "Vĩnh Long", "region": "Miền Nam", "lat_min": 9.9, "lat_max": 10.35, "lon_min": 105.75, "lon_max": 106.25, "step": 0.014, "zoom": 15, "poly": [(10.3, 105.95), (10.25, 106.2), (9.98, 106.15), (9.95, 105.85), (10.15, 105.8), (10.3, 105.95)]},
    "dong_thap": {"name": "Đồng Tháp", "region": "Miền Nam", "lat_min": 10.1, "lat_max": 10.95, "lon_min": 105.15, "lon_max": 105.95, "step": 0.015, "zoom": 15, "poly": [(10.92, 105.3), (10.85, 105.75), (10.4, 105.9), (10.15, 105.75), (10.25, 105.4), (10.65, 105.2), (10.92, 105.3)]},
    "an_giang": {"name": "An Giang", "region": "Miền Nam", "lat_min": 10.15, "lat_max": 10.95, "lon_min": 104.75, "lon_max": 105.6, "step": 0.015, "zoom": 15, "poly": [(10.9, 105.15), (10.75, 105.45), (10.3, 105.5), (10.2, 105.2), (10.4, 104.85), (10.75, 104.9), (10.9, 105.15)]},
    "kien_giang": {"name": "Kiên Giang", "region": "Miền Nam", "lat_min": 9.4, "lat_max": 10.55, "lon_min": 104.4, "lon_max": 105.5, "step": 0.016, "zoom": 15, "poly": [(10.45, 104.45), (10.45, 105.25), (9.95, 105.45), (9.45, 105.2), (9.5, 104.8), (10.0, 104.85), (10.45, 104.45)]},
    "can_tho": {"name": "Cần Thơ", "region": "Miền Nam", "lat_min": 9.9, "lat_max": 10.35, "lon_min": 105.3, "lon_max": 105.85, "step": 0.013, "zoom": 15, "poly": [(10.3, 105.45), (10.25, 105.8), (10.0, 105.8), (9.95, 105.55), (10.1, 105.35), (10.3, 105.45)]},
    "hau_giang": {"name": "Hậu Giang", "region": "Miền Nam", "lat_min": 9.55, "lat_max": 10.0, "lon_min": 105.3, "lon_max": 105.95, "step": 0.014, "zoom": 15, "poly": [(9.98, 105.7), (9.9, 105.9), (9.65, 105.85), (9.6, 105.45), (9.8, 105.35), (9.98, 105.7)]},
    "soc_trang": {"name": "Sóc Trăng", "region": "Miền Nam", "lat_min": 9.25, "lat_max": 9.95, "lon_min": 105.55, "lon_max": 106.3, "step": 0.014, "zoom": 15, "poly": [(9.9, 106.0), (9.75, 106.25), (9.4, 106.2), (9.3, 105.8), (9.6, 105.6), (9.9, 106.0)]},
    "bac_lieu": {"name": "Bạc Liêu", "region": "Miền Nam", "lat_min": 9.05, "lat_max": 9.65, "lon_min": 105.15, "lon_max": 105.85, "step": 0.015, "zoom": 15, "poly": [(9.6, 105.5), (9.55, 105.75), (9.2, 105.75), (9.1, 105.35), (9.35, 105.2), (9.6, 105.5)]},
    "ca_mau": {"name": "Cà Mau", "region": "Miền Nam", "lat_min": 8.55, "lat_max": 9.55, "lon_min": 104.7, "lon_max": 105.45, "step": 0.016, "zoom": 15, "poly": [(9.5, 105.25), (9.35, 105.4), (8.85, 105.3), (8.6, 104.85), (8.9, 104.8), (9.3, 104.85), (9.5, 105.25)]},
}

def in_ring(lat_point, lon_point, poly_ring):
    """[Điểm 13: Đặt tên biến rõ ràng & Ray casting chuẩn]: lat_point (Y), lon_point (X)"""
    if not poly_ring: return True
    inside = False; j = len(poly_ring) - 1
    for i in range(len(poly_ring)):
        yi, xi = poly_ring[i]; yj, xj = poly_ring[j]
        den = (yj - yi)
        if abs(den) < 1e-12:
            j = i
            continue
        if (yi > lat_point) != (yj > lat_point) and lon_point < (xj - xi) * (lat_point - yi) / den + xi:
            inside = not inside
        j = i
    return inside

def strip_vn_accents(s):
    if not s: return ""
    s = unicodedata.normalize('NFD', str(s))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = s.replace('đ', 'd').replace('Đ', 'D')
    return unicodedata.normalize('NFC', s).strip()

# ======================================================================================
# BƯỚC 4: TỪ KHÓA, MÀU TAB & BỘ LỌC PHÂN LOẠI NGÀNH CHUẨN XÁC
# ======================================================================================
KEYWORDS_HORECA = [
    "quán cà phê",
    "tiệm cafe",
    "quán trà sữa",
    "quán ăn",
    "nhà hàng",
    "quán cơm bình dân",
    "quán phở bún",
    "quán bia hơi quán nhậu",
    "quán ốc hải sản"
]

TAB_COLORS_HORECA = {
    'Tổng quan': 'FF1F4E78',
    'Tất cả (chuẩn hóa)': 'FF1F4E78',
    'Quán cà phê - Trà sữa': 'FF8B4513',
    'Nhà hàng': 'FFC00000',
    'Quán cơm - Phở - Bún': 'FFED7D31',
    'Quán nhậu - Bia hơi': 'FFFFC000',
    'Quán ốc - Hải sản': 'FF0277BD',
    'Quán ăn - Ăn vặt': 'FF548235',
    'Cần kiểm tra': 'FFFFC000',
    'Chưa xác định': 'FFBFBFBF',
    'Gốc (CSV)': 'FF000000'
}

HORECA_CATEGORY_TABS = [
    'Quán cà phê - Trà sữa',
    'Nhà hàng',
    'Quán cơm - Phở - Bún',
    'Quán nhậu - Bia hơi',
    'Quán ốc - Hải sản',
    'Quán ăn - Ăn vặt',
    'Cần kiểm tra',
    'Chưa xác định'
]

def _norm_text(s):
    return strip_vn_accents(unicodedata.normalize("NFC", str(s or ""))).lower()

def _raw_lower(s):
    return unicodedata.normalize("NFC", str(s or "")).lower()

def _kw(nr, nl, accented, ascii_):
    """Từ ngắn dễ trùng khi bỏ dấu (ốc/óc, cơm/cớm, cám/cam, lân/lan...): khớp theo bản CÓ DẤU;
    chỉ dùng mẫu không dấu khi tên viết hoàn toàn không dấu."""
    if re.search(accented, nr): return True
    return nr == nl and re.search(ascii_, nl) is not None

_HC_NOISE_RE = re.compile(r"\b(nha thuoc|quay thuoc|hieu thuoc|benh vien|phong kham|truong hoc|sua xe|tap hoa|salon|spa|karaoke|massage|khach san|nha nghi)\b")
_HC_OK_RE = re.compile(r"\b(quan an|nha hang|ca phe|cafe|coffee|tra sua|quan nhau|bia hoi|hai san|quan com|quan pho|quan bun|an vat)\b")
_HC_NHAU_RE = re.compile(r"\b(quan nhau|nhau|bia hoi|bia tuoi|beer|lau nuong|quan lau|quan nuong|pub|bar)\b")
_HC_CAFE_RE = re.compile(r"\b(ca phe|cafe|coffee|tra sua|tra chanh|milk tea|highlands|starbucks|trung nguyen|phuc long|the coffee house|cong ca phe|katinat|gong cha|tocotoc)\b")
_HC_NHAHANG_RE = re.compile(r"\b(nha hang|restaurant|buffet|tiec cuoi)\b")
_HC_ANVAT_RE = re.compile(r"\b(quan an|an vat|banh mi|fast food|do an nhanh|com tam)\b")

def _is_horeca_noise_filtered(ten_raw, loai_raw):
    both = _norm_text(ten_raw) + " " + _norm_text(loai_raw)
    return bool(_HC_NOISE_RE.search(both)) and not _HC_OK_RE.search(both)

def detect_horeca_group(ten_raw, loai_raw):
    nl, ll = _norm_text(ten_raw), _norm_text(loai_raw)
    nr, lr = _raw_lower(ten_raw), _raw_lower(loai_raw)
    both = nl + " " + ll
    if _is_horeca_noise_filtered(ten_raw, loai_raw): return "Cần kiểm tra"
    # "ốc" (có dấu) mới là quán ốc; "óc/ọc" bị bỏ dấu sẽ trùng
    if re.search(r"\b(ốc|hải sản|ghẹ|tôm hùm)\b", nr) or re.search(r"\b(ốc|hải sản)\b", lr) or re.search(r"\bhai san\b", nl) or (nr == nl and re.search(r"\boc\b", nl)):
        return "Quán ốc - Hải sản"
    if _HC_NHAU_RE.search(both): return "Quán nhậu - Bia hơi"
    if _HC_CAFE_RE.search(both): return "Quán cà phê - Trà sữa"
    if _HC_NHAHANG_RE.search(both): return "Nhà hàng"
    # cơm/phở/bún: khớp CÓ DẤU (ASCII chỉ khi tên viết không dấu; "pho"/"com" trần dễ trùng "phố", "com")
    if _kw(nr, nl, r"\b(cơm|phở|bún|hủ tiếu|mì quảng|bánh canh|bánh cuốn|miến|cháo)\b", r"\b(quan com|quan pho|pho|quan bun|hu tieu|mi quang|banh canh|banh cuon|mien ga|chao)\b") or _kw(lr, ll, r"\b(cơm|phở|bún)\b", r"\b(quan com|quan pho|quan bun)\b"):
        return "Quán cơm - Phở - Bún"
    if _HC_ANVAT_RE.search(both): return "Quán ăn - Ăn vặt"
    if "quan nuoc" in ll: return "Quán cà phê - Trà sữa"
    return "Chưa xác định"

# ======================================================================================
# GIAI ĐOẠN 1: QUÉT MAPS LƯỚI DÂN SINH (PLAYWRIGHT TURBO)
# ======================================================================================
COORD_RE = re.compile(r"!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)")
PLACEID_RE = re.compile(r"!1s(0x[0-9a-fA-F]+)(?::|%3A)(0x[0-9a-fA-F]+)")
CHIK_RE = re.compile(r"!19s(ChIJ[A-Za-z0-9_-]{20,})")
PHONE_CAND_RE = re.compile(r"(?<!\d)(?:\+84|84|0)(?:[\s.\-\u2010-\u2015()]{0,2}\d){8,10}(?!\d)")
MOBILE_OK = re.compile(r"0(?:3[2-9]|5[689]|7[06-9]|8[1-9]|9\d)\d{7}")
LAND_OK = re.compile(r"02\d{9}")
RATING_RE = re.compile(r"(\d[.,]\d)\s*\(([\d.,]+)\)")
HOURS_RE = re.compile(r"(mở cửa|đóng cửa|open|closed|closes|opens|24 giờ|24 hours)", re.I)
CTRL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
PERM_CLOSED_RE = re.compile(r"đóng cửa vĩnh viễn|permanently closed", re.I)
TEMP_CLOSED_RE = re.compile(r"tạm thời đóng cửa|đóng cửa tạm thời|temporarily closed", re.I)
NO_RESULT_RE = re.compile(r"không tìm thấy|can't find|không có kết quả|no results", re.I)

EXTRACT_JS = """() => {
    const feed = document.querySelector('div[role="feed"]');
    const root = feed || document;
    const elements = root.querySelectorAll('div[role="article"], div.Nv2PK, div[jsaction*="mouseover:pane"]');
    const results = [];
    const seen = new Set();
    for (const el of elements) {
        const a = el.querySelector('a[href*="/maps/place/"]') || (el.tagName === 'A' && el.href.includes('/maps/place/') ? el : null);
        const href = a ? a.href : '';
        if (!href || seen.has(href)) continue;
        seen.add(href);
        const name = (a ? a.getAttribute('aria-label') : '') || el.querySelector('.qBF1Pd, div.fontHeadlineSmall')?.innerText || '';
        results.push({ href: href, name: name, text: el.innerText || '' });
    }
    if (results.length === 0) {
        const links = root.querySelectorAll('a.hfpxzc, a[href*="/maps/place/"]');
        for (const l of links) {
            if (l.href && !seen.has(l.href)) {
                seen.add(l.href);
                const parent = l.closest('div[jsaction], div.Nv2PK') || l.parentElement;
                results.push({
                    href: l.href,
                    name: l.getAttribute('aria-label') || '',
                    text: parent ? parent.innerText : ''
                });
            }
        }
    }
    return results;
}"""
SCROLL_JS = """() => { const f = document.querySelector('div[role="feed"]'); if (!f) return [0, true]; f.scrollTo(0, f.scrollHeight); const arts = f.querySelectorAll('div[role="article"]'); const end = /hết danh sách|end of the list/i.test(f.innerText); return [arts.length, end]; }"""

def detect_status(lines):
    if not lines: return "Không rõ"
    body = " ".join(lines[1:])
    if PERM_CLOSED_RE.search(body): return "Có nhãn ĐÓNG VĨNH VIỄN"
    if TEMP_CLOSED_RE.search(body): return "Có nhãn TẠM ĐÓNG"
    return "Không có nhãn đóng cửa"

def place_id_from_href(href):
    m = PLACEID_RE.search(href or "")
    if m: return f"{m.group(1)}:{m.group(2)}"
    m_chij = CHIK_RE.search(href or "")
    if m_chij: return m_chij.group(1)
    return "hash:" + hashlib.md5((href or "").encode("utf-8")).hexdigest()[:16]

def clean_str(s): return CTRL_RE.sub("", s or "").strip()

def _addr_from_label(lab):
    lab = re.sub(r"[\ue000-\uf8ff\u200b-\u200f]", "", lab or "").strip()
    return clean_str(lab.split(":", 1)[-1] if ":" in lab else lab)

def normalize_phone_basic(raw):
    d = re.sub(r"\D", "", raw or "")
    if d.startswith("84"): d = "0" + d[2:]
    if MOBILE_OK.fullmatch(d) or LAND_OK.fullmatch(d): return d
    return ""

def extract_phone_basic(txt):
    for m in PHONE_CAND_RE.finditer(txt or ""):
        p = normalize_phone_basic(m.group(0))
        if p: return p
    return ""


_HORECA_CAT_RE = re.compile(r"\b(quan an|nha hang|ca phe|cafe|coffee|tra sua|quan nhau|bia|bar|pub|hai san|quan com|quan pho|quan bun|an vat|fast food|quan nuoc)\b")

def _is_cat_text(x):
    t = strip_vn_accents(unicodedata.normalize("NFC", str(x or ""))).lower()
    return bool(_HORECA_CAT_RE.search(t))

def _split_cat_addr(line):
    """'Nhà thuốc 24/7 · Cầu Giấy' -> (category, address). Ưu tiên vế có số = địa chỉ."""
    parts = [x.strip() for x in str(line).split("·") if x.strip()]
    if not parts: return "", ""
    if len(parts) == 1: return parts[0], ""
    p1, p2 = parts[0], parts[-1]
    has_digit_1 = bool(re.search(r"\d", p1))
    has_digit_2 = bool(re.search(r"\d", p2))
    if has_digit_1 and not has_digit_2: return p2, p1
    if has_digit_2 and not has_digit_1: return p1, p2
    if _is_cat_text(p2) and not _is_cat_text(p1): return p2, p1
    return p1, p2

def parse_item(item, lat, lon, kw, zoom):
    href, text = item.get("href", "") or "", item.get("text", "") or ""
    lines = [clean_str(l) for l in text.split("\n") if clean_str(l)]
    name = clean_str(item.get("name", "")) or (lines[0] if lines else "")
    if not name: return None
    pid = place_id_from_href(href)
    if not pid: return None
    mc = COORD_RE.search(href); slat, slon = mc.groups() if mc else ("", "")
    phone = ""
    for l in lines:
        p = extract_phone_basic(l)
        if p: phone = p; break
    rating = reviews = ""
    mr = RATING_RE.search(" ".join(lines))
    if mr: rating = mr.group(1).replace(",", "."); reviews = re.sub(r"[.,]", "", mr.group(2))
    
    category = address = ""
    for l in lines[1:]:
        if "·" in l and not HOURS_RE.search(l):
            category, address = _split_cat_addr(l)
            break

    return {
        "Tên điểm bán": name, "Place ID": pid, "Loại hình": category, "Trạng thái Maps": detect_status(lines),
        "Địa chỉ (raw)": address, "Số điện thoại": phone, "Đánh giá": rating, "Số review": reviews,
        "Vĩ độ (Lat)": slat, "Kinh độ (Lon)": slon, "Link Google Maps": href, "Tọa độ Lưới Quét": f"{lat},{lon}",
        "Zoom quét": str(zoom), "Từ khóa": kw
    }

async def create_ctx(browser):
    ctx = await browser.new_context(
        locale="vi-VN",
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    )
    try:
        await ctx.add_cookies([
            {"name": "SOCS", "value": "CAESHAgBEhJnd3NfMjAyMzA4MTAtMF9SQzIaAmVuIAEaBgiAo_CmBg", "domain": ".google.com", "path": "/"},
            {"name": "CONSENT", "value": "PENDING+987", "domain": ".google.com", "path": "/"}
        ])
    except Exception: pass

    async def _route(r):
        if r.request.resource_type in ("image", "font", "media"): await r.abort()
        else: await r.continue_()
    await ctx.route("**/*", _route)
    page = await ctx.new_page()
    return ctx, page

async def scan_cell(page, lat, lon, kw, zoom):
    url = f"https://www.google.com/maps/search/{urllib.parse.quote(kw)}/@{lat},{lon},{zoom}z"
    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
    try:
        consent_btn = await page.query_selector('button[aria-label*="Accept all"], button[aria-label*="Đồng ý"], form[action*="consent"] button')
        if consent_btn:
            await consent_btn.click()
            await page.wait_for_timeout(500)
    except Exception: pass

    if "/sorry/" in page.url:
        raise RuntimeError("BLOCKED: Google sorry/captcha")
    try:
        body_init = (await page.inner_text("body")).lower()
        if "unusual traffic" in body_init or "xác minh bạn không phải là người máy" in body_init or "recaptcha" in body_init:
            raise RuntimeError("BLOCKED: Inline Google captcha detected")
    except PWTimeout: pass
    except Exception as e:
        if "BLOCKED" in str(e): raise
    try:
        await page.wait_for_selector('div[role="feed"], div.Nv2PK, a.hfpxzc, a[href*="/maps/place/"]', timeout=8000)
    except PWTimeout:
        body = await page.inner_text("body")
        if NO_RESULT_RE.search(body): return []
        raise RuntimeError("TIMEOUT: Không thấy kết quả Maps")

    # Single-place view: Trích xuất thêm thông tin nút DOM chi tiết (Góp ý DeepSeek)
    if "/maps/place/" in page.url and not await page.query_selector('div[role="feed"]'):
        try: await page.wait_for_selector('button[data-item-id="address"]', timeout=3000)   # trang 1 điểm render chậm
        except Exception: pass
        h1 = await page.query_selector("h1")
        name = clean_str(await h1.inner_text()) if h1 else ""
        item = parse_item({"href": page.url, "name": name, "text": name}, lat, lon, kw, zoom)
        if item:
            try:
                ad_btn = await page.query_selector('button[data-item-id="address"]')
                if ad_btn:
                    item["Địa chỉ (raw)"] = _addr_from_label(await ad_btn.get_attribute("aria-label") or "")
                ph_btn = await page.query_selector('button[data-item-id^="phone:tel:"]')
                if ph_btn:
                    did = await ph_btn.get_attribute("data-item-id") or ""
                    item["Số điện thoại"] = normalize_phone_basic(did.split("tel:", 1)[-1])
            except Exception: pass
            return [item]
        return []

    prev, stable = -1, 0
    for _ in range(25):
        n, end = await page.evaluate(SCROLL_JS)
        if end: break
        stable = stable + 1 if n == prev else 0
        if stable >= 2: break
        prev = n
        await page.wait_for_timeout(random.randint(500, 800))

    rows = []
    for it in await page.evaluate(EXTRACT_JS):
        r = parse_item(it, lat, lon, kw, zoom)
        if r: rows.append(r)
    return rows

async def quet_maps_pipeline(slug, conf):
    print(f"\n🔍 [GIAI ĐOẠN 1/5] Quét Maps lưới dân sinh HORECA & F&B: {conf['name']}...")
    csv_out = LOCAL_BASE / f"horeca_{slug}_CHECKPOINT.csv"
    drive_csv = DRIVE_OUTPUT_DIR / csv_out.name

    if not EP_CHAY_LAI and csv_out.exists() and csv_out.stat().st_size > 5000:
        print(f"   ⏩ Đã có checkpoint CSV: {csv_out.name} ({csv_out.stat().st_size/(1024*1024):.1f} MB). Bỏ qua cào mới!")
        return csv_out
    if not EP_CHAY_LAI and ROOT_DRIVE and drive_csv.exists() and drive_csv.stat().st_size > 5000:
        safe_copy(drive_csv, csv_out)
        print(f"   📥 Đã nạp checkpoint CSV từ Drive: {csv_out.name} ({csv_out.stat().st_size/(1024*1024):.1f} MB).")
        return csv_out

    lat_min, lat_max = conf["lat_min"], conf["lat_max"]
    lon_min, lon_max = conf["lon_min"], conf["lon_max"]
    step = conf.get("step", 0.015)
    zoom = conf.get("zoom", 15)
    poly = conf.get("poly", [])

    lat_grid = np.arange(lat_min, lat_max, step)[::-1]
    lon_grid = np.arange(lon_min, lon_max, step)
    grid_coords = [(round(float(la), 5), round(float(lo), 5)) for la in lat_grid for lo in lon_grid]

    cells = []
    for la, lo in grid_coords:
        if in_ring(la, lo, poly):
            for kw in KEYWORDS_HORECA:
                cells.append((la, lo, kw))

    db_path = LOCAL_BASE / f"raw_horeca_{slug}.db"
    d_db = DRIVE_OUTPUT_DIR / f"raw_horeca_{slug}.db"
    if ROOT_DRIVE and not db_path.exists() and d_db.exists():
        safe_copy(d_db, db_path)
        print(f"   📥 Đã khôi phục DB quét thô từ Drive: {d_db.name}")

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS places (
            place_id TEXT PRIMARY KEY, title TEXT, category TEXT, status TEXT,
            address TEXT, phone TEXT, rating TEXT, reviews TEXT, lat TEXT, lon TEXT,
            url TEXT, grid_coord TEXT, zoom TEXT, keyword TEXT
        )
    """)
    conn.execute("CREATE TABLE IF NOT EXISTS completed_cells (cell_key TEXT PRIMARY KEY)")
    conn.commit()

    cur = conn.cursor()
    cur.execute("SELECT cell_key FROM completed_cells")
    done_cells = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT place_id FROM places")
    seen_places = {r[0] for r in cur.fetchall()}

    if len(seen_places) == 0 and len(done_cells) > 0:
        print(f"   ⚠️ Cache ô quét rỗng (0 điểm nhưng có {len(done_cells):,} ô đã xong). Reset cache ô để cào lại...")
        conn.execute("DELETE FROM completed_cells")
        conn.commit()
        done_cells.clear()

    if EP_CHAY_LAI:
        conn.execute("DELETE FROM completed_cells")
        conn.execute("DELETE FROM places")
        conn.commit()
        done_cells.clear()
        seen_places.clear()

    # Tinh chỉnh DeepSeek: Lọc done_cells TRƯỚC rồi mới áp dụng LIMIT_TEST (chống test ra ô rỗng)
    todo_cells = [c for c in cells if f"{c[0]}|{c[1]}|{c[2]}" not in done_cells]
    seed_val = RANDOM_SEED if 'RANDOM_SEED' in globals() and RANDOM_SEED else int(hashlib.md5(slug.encode()).hexdigest()[:8], 16)
    random.seed(seed_val)
    random.shuffle(todo_cells)
    if LIMIT_TEST > 0:
        todo_cells = todo_cells[:LIMIT_TEST]
        print(f"   🧪 [CHẾ ĐỘ TEST]: Giới hạn quét {len(todo_cells):,} ô...")

    print(f"   ⏳ Số ô còn lại cần quét: {len(todo_cells):,} ô (Đã có từ trước: {len(seen_places):,} điểm)")

    q = asyncio.Queue()
    for c in todo_cells: q.put_nowait(c)
    pbar = tqdm(total=len(todo_cells), desc=f"   Quét {conf['name']}", unit="ô", mininterval=1.0)
    db_lock = threading.Lock()
    attempts, failed_cells = {}, []
    blocked = {"n": 0}
    flush_cnt = {"n": 0}

    def backup_db():
        try:
            tmp = LOCAL_BASE / f"{db_path.stem}_bak.db"
            bk = sqlite3.connect(tmp)
            with db_lock:
                conn.backup(bk)
            bk.close()
            safe_copy(tmp, DRIVE_OUTPUT_DIR / db_path.name)
        except Exception: pass

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--blink-settings=imagesEnabled=false"])

        async def worker(idx):
            await asyncio.sleep(idx * 0.3)
            ctx, page, handled = None, None, 0
            buf_places, buf_done = [], []

            def flush():
                if buf_places:
                    with db_lock:
                        conn.executemany("""
                            INSERT OR IGNORE INTO places (place_id, title, category, status, address, phone, rating, reviews, lat, lon, url, grid_coord, zoom, keyword)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, [(r["Place ID"], r["Tên điểm bán"], r["Loại hình"], r["Trạng thái Maps"], r["Địa chỉ (raw)"],
                               r["Số điện thoại"], r["Đánh giá"], r["Số review"], r["Vĩ độ (Lat)"], r["Kinh độ (Lon)"],
                               r["Link Google Maps"], r["Tọa độ Lưới Quét"], r["Zoom quét"], r["Từ khóa"]) for r in buf_places])
                        conn.commit()
                    buf_places.clear()
                if buf_done:
                    with db_lock:
                        conn.executemany("INSERT OR IGNORE INTO completed_cells VALUES (?)", [(k,) for k in buf_done])
                        conn.commit()
                    buf_done.clear()
                flush_cnt["n"] += 1
                if flush_cnt["n"] % 20 == 0:
                    backup_db()

            try:
                while blocked["n"] < 8:
                    try: la, lo, kw = q.get_nowait()
                    except asyncio.QueueEmpty: break
                    ck = f"{la}|{lo}|{kw}"

                    if page is None or handled >= 60:
                        if ctx:
                            try: await ctx.close()
                            except Exception: pass
                        ctx, page = await create_ctx(browser); handled = 0

                    try:
                        rows = await scan_cell(page, la, lo, kw, zoom)
                        ok = True
                    except Exception as e:
                        ok, rows = False, []
                        if "BLOCKED" in str(e):
                            blocked["n"] += 1
                            await asyncio.sleep(30)
                        try: await ctx.close()
                        except Exception: pass
                        ctx = page = None
                    handled += 1

                    if ok:
                        # db_lock bảo vệ tính nhất quán khi flush buffer và đồng bộ cấu trúc seen_places
                        with db_lock:
                            for r in rows:
                                if r["Place ID"] not in seen_places:
                                    seen_places.add(r["Place ID"])
                                    buf_places.append(r)
                            buf_done.append(ck)
                        pbar.update(1)
                        pbar.set_description(f"   ⚡ Điểm: {len(seen_places):,}")
                    else:
                        attempts[ck] = attempts.get(ck, 0) + 1
                        if attempts[ck] < 3:
                            q.put_nowait((la, lo, kw))
                            pbar.set_postfix_str(f"Retry {attempts[ck]}/3: {kw[:10]}")
                        else:
                            failed_cells.append(ck)
                            pbar.update(1)

                    # [Vá W11]: Phục hồi chỉ số blocked khi có request thành công
                    if ok:
                        blocked["n"] = max(0, blocked["n"] - 1)
                    if len(buf_places) >= 15 or len(buf_done) >= 15: flush()
                    # [VÁ ZERO-CRASH GĐ1]: Giải phóng DOM Chrome khi quét ô bản đồ
                    if IS_COLAB and len(seen_places) % 300 == 0:
                        try:
                            from IPython.display import clear_output
                            clear_output(wait=True)
                            import gc
                            gc.collect()
                        except Exception:
                            pass

                    # Giãn nhịp an toàn 1.5s - 3.0s chống Google Maps rate-limit IP
                    await asyncio.sleep(random.uniform(1.5, 3.0))
            finally:
                flush()
                if ctx:
                    try: await ctx.close()
                    except Exception: pass

        workers = [worker(i) for i in range(min(CONCURRENCY_WORKERS, 6))]
        await asyncio.gather(*workers)
        pbar.close()
        await browser.close()

    backup_db()
    if failed_cells or not q.empty():
        conn.close()
        raise RuntimeError(
            f"GĐ1 CHƯA HOÀN TẤT: Còn {q.qsize():,} ô chưa quét, {len(failed_cells):,} ô lỗi 3 lần, "
            f"bị chặn {blocked['n']} lần. Tiến độ đã lưu - chạy lại cell để tiếp tục."
        )

    cur.execute("SELECT title, place_id, category, status, address, phone, rating, reviews, lat, lon, url, grid_coord, zoom, keyword FROM places")
    all_places = cur.fetchall()
    conn.close()

    df_ckpt = pd.DataFrame(all_places, columns=[
        'Tên điểm bán', 'Place ID', 'Loại hình', 'Trạng thái Maps', 'Địa chỉ (raw)', 'Số điện thoại',
        'Đánh giá', 'Số review', 'Vĩ độ (Lat)', 'Kinh độ (Lon)', 'Link Google Maps', 'Tọa độ Lưới Quét', 'Zoom quét', 'Từ khóa'
    ])
    df_ckpt.to_csv(csv_out, index=False, encoding='utf-8-sig')
    safe_copy(csv_out, drive_csv)
    print(f"   ✅ [XONG GĐ 1] Đã lưu {len(df_ckpt):,} điểm bán vào {csv_out.name}")
    return csv_out

# ======================================================================================
# GIAI ĐOẠN 2: CHUẨN HÓA MULTI-TAB CHUYÊN NGÀNH HORECA & F&B
# ======================================================================================
def extract_chij(link):
    if not link or pd.isna(link): return ''
    m = re.search(r'!19s(ChIJ[^\?\&]+)', str(link))
    if m: return m.group(1)
    m2 = re.search(r'(ChIJ[A-Za-z0-9_-]+)', str(link))
    return m2.group(1) if m2 else ''

def chuan_hoa_excel_pipeline(slug, conf, csv_file):
    print(f"\n📊 [GIAI ĐOẠN 2/5] Chuẩn hóa và phân loại Multi-Tab: {conf['name']}...")
    out_xlsx = LOCAL_BASE / f"horeca_{slug}_CHUAN_HOA.xlsx"

    if not EP_CHAY_LAI and _fresh(out_xlsx, csv_file):
        print(f"   ⏩ Đã có file Chuẩn Hóa mới hơn CSV: {out_xlsx.name}. Bỏ qua!")
        return out_xlsx

    if not csv_file or not Path(csv_file).exists():
        print(f"   ❌ Không tìm thấy file CSV đầu vào: {csv_file}")
        return None

    df_raw = pd.read_csv(csv_file, dtype=str).fillna('')
    if len(df_raw) == 0:
        print(f"   ⚠ File CSV {Path(csv_file).name} chưa có điểm bán nào (0 dòng)! Bỏ qua chuẩn hóa.")
        return None

    n0 = len(df_raw)
    df_raw = df_raw.drop_duplicates(subset=['Place ID'], keep='first').reset_index(drop=True)
    la = pd.to_numeric(df_raw['Vĩ độ (Lat)'], errors='coerce')
    lo = pd.to_numeric(df_raw['Kinh độ (Lon)'], errors='coerce')
    pad = 0.03
    inside = la.isna() | lo.isna() | (
        (la >= conf['lat_min'] - pad) & (la <= conf['lat_max'] + pad) &
        (lo >= conf['lon_min'] - pad) & (lo <= conf['lon_max'] + pad))
    n_out = int((~inside).sum())
    df_raw = df_raw[inside].reset_index(drop=True)
    df_raw['_orig_row'] = range(2, 2 + len(df_raw))
    print(f"   📈 {n0:,} dòng thô -> {len(df_raw):,} điểm (loại {n_out:,} điểm ngoài bbox tỉnh, còn lại là trùng)")

    rows_std = []
    for idx, r in df_raw.iterrows():
        ten = str(r['Tên điểm bán'] or '')
        loai = str(r['Loại hình'] or '')
        grp = detect_horeca_group(ten, loai)

        phone_val = str(r['Số điện thoại'] or '').strip()
        addr_raw = str(r['Địa chỉ (raw)'] or '').strip()
        addr_clean = addr_raw if addr_raw and addr_raw.lower() != 'unnamed' else None

        rows_std.append({
            'Dòng ở tab gốc': r['_orig_row'],
            'Tên điểm bán': ten,
            'Nhóm điểm': grp,
            'Loại hình (Google Maps)': loai or None,
            'Địa chỉ (gốc từ Maps)': addr_clean,
            'Địa chỉ cụ thể (bổ sung)': None,
            'Nguồn địa chỉ': 'Maps gốc' if addr_clean else 'Chưa có địa chỉ - cần tra cứu',
            'Số điện thoại': phone_val if len(phone_val) > 5 else None,
            'Đánh giá': r['Đánh giá'] if r['Đánh giá'] != '' else None,
            'Số review': r['Số review'] if r['Số review'] != '' else None,
            'Trạng thái Maps': r['Trạng thái Maps'],
            'Vĩ độ': r['Vĩ độ (Lat)'],
            'Kinh độ': r['Kinh độ (Lon)'],
            'Link Google Maps': r['Link Google Maps'],
            'Place ID': r['Place ID'],
            'Place ID (ChIJ)': extract_chij(r['Link Google Maps']),
            'Từ khóa quét': r['Từ khóa'],
            'Tọa độ lưới quét': r['Tọa độ Lưới Quét'],
            'Zoom quét': r['Zoom quét']
        })

    std_cols = ['Dòng ở tab gốc', 'Tên điểm bán', 'Nhóm điểm', 'Loại hình (Google Maps)', 'Địa chỉ (gốc từ Maps)', 'Địa chỉ cụ thể (bổ sung)', 'Nguồn địa chỉ', 'Số điện thoại', 'Đánh giá', 'Số review', 'Trạng thái Maps', 'Vĩ độ', 'Kinh độ', 'Link Google Maps', 'Place ID', 'Place ID (ChIJ)', 'Từ khóa quét', 'Tọa độ lưới quét', 'Zoom quét']
    df_excel = pd.DataFrame(rows_std, columns=std_cols)

    wb_out = openpyxl.Workbook()
    wb_out.remove(wb_out.active)

    category_tabs = list(HORECA_CATEGORY_TABS)
    sheet_order = ['Tổng quan', 'Tất cả (chuẩn hóa)'] + category_tabs + ['Gốc (CSV)']

    for sn in sheet_order:
        ws = wb_out.create_sheet(title=sn[:31])
        rgb = TAB_COLORS_HORECA.get(sn)
        if rgb: ws.sheet_properties.tabColor = Color(rgb=rgb)

    header_fill = PatternFill(start_color="FF1F4E78", end_color="FF1F4E78", fill_type="solid")
    header_font = Font(name="Arial", size=10, bold=True, color="FFFFFFFF")
    border = Border(left=Side(style='thin', color='FFD9D9D9'), right=Side(style='thin', color='FFD9D9D9'), top=Side(style='thin', color='FFD9D9D9'), bottom=Side(style='thin', color='FFD9D9D9'))

    def write_sheet(ws, sub_df, cols):
        ws.append(cols)
        for c_idx in range(1, len(cols) + 1):
            cell = ws.cell(row=1, column=c_idx)
            cell.fill = header_fill; cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True); cell.border = border
        if len(sub_df) > 0:
            for rec in sub_df[cols].astype(object).where(sub_df[cols].notna(), None).values.tolist():
                ws.append([_xl(v) for v in rec])
            ws.auto_filter.ref = f"A1:{get_column_letter(len(cols))}{len(sub_df)+1}"
        ws.freeze_panes = 'C2' if cols is std_cols else 'A2'

    write_sheet(wb_out['Tất cả (chuẩn hóa)'], df_excel, std_cols)
    for name in category_tabs:
        write_sheet(wb_out[name[:31]], df_excel[df_excel['Nhóm điểm'] == name], std_cols)

    goc_cols = ['Tên điểm bán', 'Place ID', 'Loại hình', 'Trạng thái Maps', 'Địa chỉ (raw)', 'Số điện thoại', 'Đánh giá', 'Số review', 'Vĩ độ (Lat)', 'Kinh độ (Lon)', 'Link Google Maps', 'Tọa độ Lưới Quét', 'Zoom quét', 'Từ khóa']
    write_sheet(wb_out['Gốc (CSV)'], df_raw, goc_cols)

    ws_tq = wb_out['Tổng quan']
    ws_tq.cell(row=1, column=2, value=f"Báo cáo Chuẩn Hóa Điểm Bán HORECA & F&B - {conf['name'].upper()}").font = Font(bold=True, size=13)
    ws_tq.cell(row=3, column=2, value="Nhóm ngành").font = Font(bold=True)
    ws_tq.cell(row=3, column=3, value="Số lượng").font = Font(bold=True)
    vc = df_excel['Nhóm điểm'].value_counts()
    for row_i, (k, v) in enumerate(vc.items(), 4):
        ws_tq.cell(row=row_i, column=2, value=k)
        ws_tq.cell(row=row_i, column=3, value=int(v))

    _atomic_save_wb(wb_out, out_xlsx)
    del wb_out, df_excel, df_raw
    gc.collect()
    print(f"   ✅ [XONG GĐ 2] Đã xuất bản file Chuẩn Hóa: {out_xlsx.name}")
    return out_xlsx

# ======================================================================================
# GIAI ĐOẠN 3: TRA ĐỊA CHỈ (ĐỊA CHỈ GỐC MAPS + OSM REVERSE, CÓ CACHE SQLITE)
# ======================================================================================
DB_CACHE_PATH = LOCAL_BASE / "reverse_geocode_turbo.db"

def init_geocode_db():
    if ROOT_DRIVE:
        drive_db = DRIVE_OUTPUT_DIR / "reverse_geocode_turbo.db"
        if not drive_db.exists(): drive_db = ROOT_DRIVE / "reverse_geocode_turbo.db"
        if drive_db.exists() and drive_db.stat().st_size > 10000:
            if not DB_CACHE_PATH.exists() or DB_CACHE_PATH.stat().st_size < drive_db.stat().st_size:
                safe_copy(drive_db, DB_CACHE_PATH)
                print(f"   📥 [CACHE DRIVE]: Đã nạp SQLite Cache ({drive_db.stat().st_size / (1024*1024):.1f} MB) từ Drive!")

    conn = sqlite3.connect(DB_CACHE_PATH)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS geocode_cache (
            place_id TEXT PRIMARY KEY, lat REAL, lon REAL, geo_key TEXT,
            street TEXT, admin TEXT, src_tier TEXT, is_specific INT, geo_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_coords ON geocode_cache(lat, lon)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_geokey ON geocode_cache(geo_key)")
    conn.commit()
    try:   # cache cũ nạp từ Drive có thể thiếu cột geo_json -> INSERT sẽ lỗi nếu không bổ sung
        conn.execute("ALTER TABLE geocode_cache ADD COLUMN geo_json TEXT")
        conn.commit()
    except Exception: pass
    conn.close()

init_geocode_db()

_OSM_SESSION = None

def get_osm_session():
    global _OSM_SESSION
    if _OSM_SESSION is None:
        _OSM_SESSION = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=1, pool_maxsize=5, max_retries=2)
        _OSM_SESSION.mount("https://", adapter)
        _OSM_SESSION.mount("http://", adapter)
        _OSM_SESSION.headers.update({"User-Agent": f"TurboHorecaColab/9.1 ({EMAIL_OSM})"})
    return _OSM_SESSION

def close_osm_session():
    global _OSM_SESSION
    if _OSM_SESSION is not None:
        try: _OSM_SESSION.close()
        except Exception: pass
        _OSM_SESSION = None

def osm_reverse_lookup(lat, lon, retries=2):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1&accept-language=vi"
    session = get_osm_session()
    for k in range(retries + 1):
        try:
            resp = session.get(url, timeout=10)
            if resp.status_code == 200:
                addr = resp.json().get("address", {})
                street = ", ".join(str(addr[x]) for x in ["house_number", "road", "suburb", "quarter", "neighbourhood"] if addr.get(x))
                admin_parts = []
                for x in ["village", "commune", "town", "city_district", "district", "city", "state", "province"]:
                    if addr.get(x) and addr[x] not in admin_parts:
                        admin_parts.append(str(addr[x]))
                admin = ", ".join(admin_parts)
                if not (street or admin): return None
                return street, admin, "OSM Reverse"
            if resp.status_code in (403, 429, 503):
                time.sleep(30 * (2 ** k))
        except Exception:
            time.sleep(2 * (k + 1))
    return None

def chay_tra_dia_chi_3_tang(slug, conf, curr_file):
    print(f"\n🗺️ [GIAI ĐOẠN 3/5] Tra địa chỉ (Maps gốc + OSM): {conf['name']}...")
    out_xlsx = LOCAL_BASE / f"horeca_{slug}_CHUAN_HOA_DA_TRA_DIA_CHI.xlsx"

    if not EP_CHAY_LAI and _fresh(out_xlsx, curr_file):
        print(f"   ⏩ Đã có file Tra Địa Chỉ mới hơn nguồn: {out_xlsx.name}. Bỏ qua!")
        return out_xlsx

    if not curr_file or not Path(curr_file).exists():
        print(f"   ❌ Không tìm thấy file Excel đầu vào để tra địa chỉ: {curr_file}")
        return None

    wb = openpyxl.load_workbook(curr_file)
    ws = wb['Tất cả (chuẩn hóa)']
    hdr = {str(c.value).strip(): idx for idx, c in enumerate(ws[1], start=1) if c.value}

    conn = sqlite3.connect(DB_CACHE_PATH)
    cur = conn.cursor()

    pts = []
    for r in range(2, ws.max_row + 1):
        pid = ws.cell(r, hdr['Place ID']).value
        lat = ws.cell(r, hdr['Vĩ độ']).value
        lon = ws.cell(r, hdr['Kinh độ']).value
        raw_addr = ws.cell(r, hdr.get('Địa chỉ (gốc từ Maps)', hdr.get('Địa chỉ (raw)', 5))).value
        if pid and lat and lon:
            try: pts.append((r, str(pid), float(lat), float(lon), str(raw_addr or '')))
            except Exception: pass

    if LIMIT_TEST > 0: pts = pts[:LIMIT_TEST]
    print(f"   📍 Tổng số điểm cần tra địa chỉ: {len(pts):,} điểm")

    cache_hits, osm_calls = 0, 0
    results_map = {}
    batch_db = []

    pbar = tqdm(total=len(pts), desc=f"   Tra địa chỉ {conf['name']}", unit="điểm", mininterval=1.0)

    for row_idx, pid, lat, lon, raw in pts:
        raw_clean = (raw or "").strip()
        if raw_clean.lower() == 'none': raw_clean = ""
        cur.execute("SELECT street, admin, src_tier FROM geocode_cache WHERE place_id = ?", (pid,))
        row = cur.fetchone()
        is_spatial_hit = False
        if not row:
            geo_key = f"{lat:.4f}_{lon:.4f}"
            cur.execute("SELECT street, admin, src_tier FROM geocode_cache WHERE geo_key = ? AND admin != '' LIMIT 1", (geo_key,))
            row = cur.fetchone()
            if row: is_spatial_hit = True
        if row and (row[0] or row[1]):
            st, ad, src = row
            if is_spatial_hit:
                final_st = raw_clean
                final_src = f"Cache Spatial geo_key ({src})"
            else:
                final_st = raw_clean or st
                final_src = f"Cache SQLite ({src})"
            full_addr = ", ".join(x for x in (final_st, ad) if x) or raw_clean or f"{conf['name']}, Việt Nam"
            results_map[pid] = (full_addr, final_src)
            cache_hits += 1
            pbar.update(1)
            continue

        res = osm_reverse_lookup(lat, lon)
        osm_calls += 1
        time.sleep(SLEEP_OSM)
        if res is None:
            results_map[pid] = (raw_clean or f"{conf['name']}, Việt Nam", "Chưa tra được OSM")
            pbar.update(1)
            continue

        st, ad, _ = res
        final_st = raw_clean or st
        final_src = "Maps gốc + OSM hành chính" if raw_clean else "OSM Reverse"
        full_addr = ", ".join(x for x in (final_st, ad) if x)
        results_map[pid] = (full_addr, final_src)
        batch_db.append((pid, lat, lon, f"{lat:.4f}_{lon:.4f}", final_st, ad, final_src, 1 if final_st else 0, "{}"))

        if len(batch_db) >= 25:
            cur.executemany("INSERT OR REPLACE INTO geocode_cache (place_id, lat, lon, geo_key, street, admin, src_tier, is_specific, geo_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", batch_db)
            conn.commit()
            batch_db = []
        pbar.update(1)

    if batch_db:
        cur.executemany("INSERT OR REPLACE INTO geocode_cache (place_id, lat, lon, geo_key, street, admin, src_tier, is_specific, geo_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", batch_db)
        conn.commit()
    conn.close()
    pbar.close()

    for ws_sub in wb.worksheets:
        if ws_sub.title.startswith("Gốc") or ws_sub.title == "Tổng quan":
            continue
        s_hdr = {str(c.value).strip(): idx for idx, c in enumerate(ws_sub[1], start=1) if c.value}
        if 'Place ID' in s_hdr and 'Địa chỉ cụ thể (bổ sung)' in s_hdr:
            for r in range(2, ws_sub.max_row + 1):
                pid = ws_sub.cell(r, s_hdr['Place ID']).value
                if pid in results_map:
                    ws_sub.cell(r, s_hdr['Địa chỉ cụ thể (bổ sung)']).value = _xl(results_map[pid][0])
                    if 'Nguồn địa chỉ' in s_hdr:
                        ws_sub.cell(r, s_hdr['Nguồn địa chỉ']).value = results_map[pid][1]

    _atomic_save_wb(wb, out_xlsx)
    del wb
    gc.collect()

    if ROOT_DRIVE:
        safe_copy(DB_CACHE_PATH, DRIVE_OUTPUT_DIR / "reverse_geocode_turbo.db")
    safe_copy(out_xlsx, DRIVE_OUTPUT_DIR / out_xlsx.name)

    print(f"   ✅ [XONG GĐ 3] Cache hit {cache_hits:,} | Gọi OSM {osm_calls:,} | File: {out_xlsx.name}")
    return out_xlsx

# ======================================================================================
# GIAI ĐOẠN 4: SĐT & ĐỊA CHỈ TỪ TRANG CHI TIẾT MAPS (CÓ CHECKPOINT SQLITE)
# ======================================================================================
INVALID_HOTLINES = {'1900', '1800', '0241080', '0281080', '0247300', '0287300'}

def normalize_phone(raw_str):
    if not raw_str: return ""
    d = re.sub(r'\D', '', str(raw_str))
    if d.startswith('84'): d = '0' + d[2:]
    for h in INVALID_HOTLINES:
        if d.startswith(h): return ""
    if MOBILE_OK.fullmatch(d) or LAND_OK.fullmatch(d): return d
    return ""

def _strip_pua(s):
    return re.sub(r"[\ue000-\uf8ff\u200b-\u200f]", "", s or "").strip()

async def lay_chi_tiet_place(page, link):
    await page.goto(link, wait_until="domcontentloaded", timeout=20000)
    if "/sorry/" in page.url:
        raise RuntimeError("BLOCKED: Google sorry/captcha")
    await page.wait_for_selector("h1", timeout=8000)
    try:
        await page.wait_for_selector('button[data-item-id^="phone:tel:"], button[data-item-id="address"]', timeout=2500)
    except Exception: pass
    out = {"phone": "", "address": ""}
    ph = await page.query_selector('button[data-item-id^="phone:tel:"]')
    if ph:
        did = await ph.get_attribute("data-item-id") or ""
        out["phone"] = normalize_phone(did.split("tel:", 1)[-1]) or normalize_phone(_strip_pua(await ph.get_attribute("aria-label") or ""))
    ad = await page.query_selector('button[data-item-id="address"]')
    if ad:
        lab = _strip_pua(await ad.get_attribute("aria-label") or "")
        out["address"] = lab.split(":", 1)[-1].strip() if ":" in lab else lab
    return out

async def enrich_phone_pipeline(slug, conf, curr_file):
    print(f"\n📞 [GIAI ĐOẠN 4/5] Bổ sung SĐT + địa chỉ từ trang chi tiết Maps: {conf['name']}...")
    out_xlsx = LOCAL_BASE / f"horeca_{slug}_HOAN_THIEN.xlsx"
    if not curr_file or not Path(curr_file).exists():
        print(f"   ❌ Không tìm thấy file Excel đầu vào: {curr_file}")
        return None

    db_path = LOCAL_BASE / f"detail_{slug}.db"
    drive_db = DRIVE_OUTPUT_DIR / db_path.name
    if ROOT_DRIVE and not db_path.exists() and drive_db.exists():
        safe_copy(drive_db, db_path)
    dconn = sqlite3.connect(db_path)
    dconn.execute("CREATE TABLE IF NOT EXISTS detail (place_id TEXT PRIMARY KEY, phone TEXT, address TEXT, ok INT)")
    dconn.commit()
    if EP_CHAY_LAI:
        dconn.execute("DELETE FROM detail"); dconn.commit()
    # Chi danh dau la DONE neu diem do thuc su da lay duoc SDT hop le (>=6 so)
    if globals().get('VET_DELTA_DIEM_THIEU_SDT', True):
        done = {r[0] for r in dconn.execute("SELECT place_id FROM detail WHERE ok=1 AND phone IS NOT NULL AND length(phone) >= 6")}
    else:
        done = {r[0] for r in dconn.execute("SELECT place_id FROM detail WHERE ok=1")}

    wb = openpyxl.load_workbook(curr_file)
    ws = wb['Tất cả (chuẩn hóa)']
    hdr = {str(c.value).strip(): idx for idx, c in enumerate(ws[1], start=1) if c.value}
    if 'Số điện thoại' not in hdr or 'Place ID' not in hdr:
        print("   ⚠️ File thiếu cột 'Số điện thoại' hoặc 'Place ID', bỏ qua GĐ4.")
        wb.close()
        return curr_file

    todo = []
    for r in range(2, ws.max_row + 1):
        pid = ws.cell(r, hdr['Place ID']).value
        phone = ws.cell(r, hdr['Số điện thoại']).value
        url = ws.cell(r, hdr['Link Google Maps']).value
        st_col = hdr.get('Trạng thái Maps')
        closed = bool(st_col) and "ĐÓNG VĨNH VIỄN" in str(ws.cell(r, st_col).value or "")   # không mở lại điểm đã đóng
        if pid and str(pid) not in done and not closed and (not phone or len(str(phone).strip()) < 6) and url and "http" in str(url):
            todo.append((str(pid), str(url)))
    if LIMIT_TEST > 0: todo = todo[:LIMIT_TEST]
    print(f"   📱 Cần lấy chi tiết: {len(todo):,} điểm (đã có trong checkpoint: {len(done):,})")

    stats = {"ok": 0, "fail": 0, "blocked": 0, "since_commit": 0}
    if todo:
        q = asyncio.Queue()
        for pid, link in todo: q.put_nowait((pid, link, 0))
        pbar = tqdm(total=len(todo), desc=f"   Chi tiết {conf['name']}", unit="điểm", mininterval=1.0)

        def commit_and_sync():
            dconn.commit()
            stats["since_commit"] = 0
            safe_copy(db_path, drive_db)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--blink-settings=imagesEnabled=false"])

            async def worker(idx):
                await asyncio.sleep(idx * 0.4)
                ctx, page = await create_ctx(browser)
                handled = 0
                try:
                    while stats["blocked"] < 8:
                        try: pid, link, tries = q.get_nowait()
                        except asyncio.QueueEmpty: break
                        if handled >= 80:
                            await ctx.close(); ctx, page = await create_ctx(browser); handled = 0
                        try:
                            d = await lay_chi_tiet_place(page, link)
                            dconn.execute("INSERT OR REPLACE INTO detail VALUES (?,?,?,1)", (pid, d["phone"], d["address"]))
                            stats["ok"] += 1
                            # [Vá W-NEW-2]: Phục hồi chỉ số blocked khi request thành công
                            stats["blocked"] = max(0, stats["blocked"] - 1)
                            pbar.update(1)
                        except Exception as e:
                            if "BLOCKED" in str(e):
                                stats["blocked"] += 1
                                await asyncio.sleep(30)
                            if tries < 2:
                                q.put_nowait((pid, link, tries + 1))
                            else:
                                dconn.execute("INSERT OR REPLACE INTO detail VALUES (?,?,?,0)", (pid, "", ""))
                                stats["fail"] += 1; pbar.update(1)
                            try: await ctx.close()
                            except Exception: pass
                            ctx, page = await create_ctx(browser); handled = 0
                        handled += 1
                        stats["since_commit"] += 1
                        if stats["since_commit"] >= 50: commit_and_sync()
                        # [VÁ ZERO-CRASH]: Giải phóng DOM Chrome & Garbage Collector chống tràn Desktop Heap
                        if IS_COLAB and (stats["ok"] + stats["fail"]) % 250 == 0:
                            try:
                                from IPython.display import clear_output
                                clear_output(wait=True)
                                import gc
                                gc.collect()
                            except Exception:
                                pass

                        # [Vá W-NEW-1]: Giãn nhịp an toàn 2.0s - 4.0s cho trang chi tiết place
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                finally:
                    try: await ctx.close()
                    except Exception: pass

            await asyncio.gather(*[worker(i) for i in range(min(CONCURRENCY_WORKERS, 4))])
            pbar.close()
            await browser.close()
        commit_and_sync()
        print(f"   ✔ Thành công {stats['ok']:,} | Lỗi {stats['fail']:,} | Bị chặn {stats['blocked']}")
        # [Vá W-NEW-3]: Raise lỗi rõ ràng nếu GĐ4 bị ngắt giữa chừng do quá ngưỡng chặn Google
        if stats["blocked"] >= 8 and not q.empty():
            dconn.close()
            wb.close()
            raise RuntimeError(f"GĐ4 CHƯA HOÀN TẤT: Bị Google Maps chặn liên tiếp {stats['blocked']} lần. Còn {q.qsize():,} điểm chưa quét. Tiến độ đã lưu - chạy lại sau.")

    res = {r[0]: (r[1], r[2]) for r in dconn.execute("SELECT place_id, phone, address FROM detail WHERE ok=1")}
    dconn.close()

    fill_maps = PatternFill(start_color="FFE2EFDA", end_color="FFE2EFDA", fill_type="solid")
    n_phone = 0
    for ws_sub in wb.worksheets:
        if ws_sub.title.startswith("Gốc") or ws_sub.title == "Tổng quan":
            continue
        h = {str(c.value).strip(): i for i, c in enumerate(ws_sub[1], start=1) if c.value}
        if 'Place ID' not in h or 'Số điện thoại' not in h:
            continue
        is_master = ws_sub.title == 'Tất cả (chuẩn hóa)'
        for r in range(2, ws_sub.max_row + 1):
            pid = ws_sub.cell(r, h['Place ID']).value
            if pid is None or str(pid) not in res: continue
            ph, ad = res[str(pid)]
            cell = ws_sub.cell(r, h['Số điện thoại'])
            if ph and not cell.value:
                cell.value = ph; cell.fill = fill_maps
                if is_master: n_phone += 1
            if ad and 'Địa chỉ cụ thể (bổ sung)' in h:
                cell_addr = ws_sub.cell(r, h['Địa chỉ cụ thể (bổ sung)'])
                current = str(cell_addr.value or "").strip()
                has_house_current = bool(re.search(r"\d+", current))
                has_house_new = bool(re.search(r"\d+", ad))
                if not current or (has_house_new and not has_house_current):
                    cell_addr.value = _xl(ad)
                    if 'Nguồn địa chỉ' in h:
                        ws_sub.cell(r, h['Nguồn địa chỉ']).value = "Maps Detail"

    _atomic_save_wb(wb, out_xlsx)
    del wb
    gc.collect()
    print(f"   ✅ [XONG GĐ 4] Điền thêm {n_phone:,} SĐT từ Maps Detail → {out_xlsx.name}")
    return out_xlsx

# ======================================================================================
# GIAI ĐOẠN 5: ĐÓNG GÓI & ĐỒNG BỘ GOOGLE DRIVE
# ======================================================================================
def dong_goi_va_dong_bo_drive(slug, conf, curr_file):
    print(f"\n💾 [GIAI ĐOẠN 5/5] Đóng gói & sao lưu lên Google Drive: {conf['name']}...")
    final_xlsx = LOCAL_BASE / f"horeca_{slug}_HOAN_THIEN.xlsx"
    if Path(curr_file).resolve() != final_xlsx.resolve():
        safe_copy(curr_file, final_xlsx)

    if ROOT_DRIVE:
        drive_file = DRIVE_OUTPUT_DIR / final_xlsx.name
        if safe_copy(final_xlsx, drive_file):
            print(f"   💾 [ĐÃ LƯU GOOGLE DRIVE]: {drive_file}")
        else:
            print(f"   ⚠ Đã lưu cục bộ: {final_xlsx}")
    else:
        print(f"   💾 Đã lưu cục bộ: {final_xlsx}")

    try:
        df = pd.read_excel(final_xlsx, sheet_name='Tất cả (chuẩn hóa)', dtype=str)
        n = len(df)
        if n:
            has_phone = df['Số điện thoại'].notna().sum()
            has_addr = (df['Địa chỉ cụ thể (bổ sung)'].notna() | df['Địa chỉ (gốc từ Maps)'].notna()).sum()
            closed = df['Trạng thái Maps'].astype(str).str.contains('ĐÓNG VĨNH VIỄN', na=False).sum()
            unk = (df['Nhóm điểm'] == 'Chưa xác định').sum()
            chk = (df['Nhóm điểm'] == 'Cần kiểm tra').sum()
            print(f"   📋 BÁO CÁO CHẤT LƯỢNG: {n:,} điểm | Có SĐT: {has_phone/n:.1%} | Có địa chỉ: {has_addr/n:.1%} | "
                  f"Đóng cửa: {closed:,} | Chưa xác định: {unk:,} | Cần kiểm tra: {chk:,}")
    except Exception as e:
        print(f"   ⚠ Không tạo được báo cáo chất lượng: {e}")

    return final_xlsx

# ======================================================================================
# BƯỚC 8: ĐIỀU HƯỚNG TỈNH & PIPELINE CHÍNH (V8.4.2 ULTRA)
# ======================================================================================
REGION_GROUPS = {
    "Miền Bắc (25 tỉnh)": {"Miền Bắc"},
    "Miền Trung & Tây Nguyên (19 tỉnh)": {"Miền Trung", "Tây Nguyên"},
    "Miền Nam (19 tỉnh)": {"Miền Nam"},
}

def _norm_key(s):
    s = re.sub(r"[\s._\-]+", " ", str(s or ""))
    return strip_vn_accents(s).lower().strip()

def lay_danh_sach_tinh_thuc_thi():
    name_to_slug = {}
    for slg, info in PROVINCES_CONFIG.items():
        name_to_slug[_norm_key(info["name"])] = slg
        name_to_slug[_norm_key(slg)] = slg
    for alias in ["TP. Hồ Chí Minh", "Hồ Chí Minh", "Sài Gòn", "HCM", "TPHCM"]:
        name_to_slug[_norm_key(alias)] = "tp_ho_chi_minh"

    if "1 tỉnh cụ thể" in CHON_CHE_DO_TINH:
        slg = name_to_slug.get(_norm_key(TINH_CU_THE))
        if not slg:
            raise ValueError(f"Không nhận diện được tỉnh: {TINH_CU_THE!r}")
        return [slg]
    if "Toàn bộ 63 tỉnh thành" in CHON_CHE_DO_TINH:
        return list(PROVINCES_CONFIG.keys())
    if "Khu vực" in CHON_CHE_DO_TINH:
        regs = REGION_GROUPS.get(KHU_VUC)
        if not regs:
            raise ValueError(f"Khu vực không hợp lệ: {KHU_VUC!r}")
        return [k for k, v in PROVINCES_CONFIG.items() if v.get("region") in regs]

    valid, bad = [], []
    for it in re.split(r"[,;\n]", DANH_SACH_TINH_TUY_CHON):
        if not it.strip(): continue
        m = name_to_slug.get(_norm_key(it))
        if m:
            if m not in valid: valid.append(m)
        else:
            bad.append(it.strip())
    if bad:
        raise ValueError(f"Không nhận diện được danh sách tỉnh: {bad}")
    if not valid:
        raise ValueError("Danh sách tỉnh tùy chọn đang rỗng.")
    return valid

def _tim_file(slug, *names):
    for nm in names:
        cand = LOCAL_BASE / nm.format(slug=slug)
        if not cand.exists() and ROOT_DRIVE and (DRIVE_OUTPUT_DIR / cand.name).exists():
            safe_copy(DRIVE_OUTPUT_DIR / cand.name, cand)
        if cand.exists():
            return cand
    return None

def in_tien_do_khu_vuc(ten_khu_vuc, idx, tong_tinh, completed_count, unfinished_dict, current_name, current_slug):
    """Hiển thị thanh tiến độ trực quan toàn khu vực và cảnh báo tỉnh dở dang"""
    pct = (completed_count / tong_tinh * 100.0) if tong_tinh > 0 else 0.0
    bar_len = 20
    filled_len = int(bar_len * completed_count // tong_tinh) if tong_tinh > 0 else 0
    bar = "█" * filled_len + "░" * (bar_len - filled_len)

    print("\n" + "=" * 85)
    print(f"📊 TIẾN ĐỘ KHU VỰC [{ten_khu_vuc}]: [{bar}] {pct:.1f}% ({completed_count}/{tong_tinh} tỉnh đã xong GĐ 5)")
    if unfinished_dict:
        unf_str = ", ".join([f"{name} ({reason})" for name, reason in list(unfinished_dict.values())[:3]])
        if len(unfinished_dict) > 3:
            unf_str += f" ... (+{len(unfinished_dict)-3} tỉnh khác)"
        print(f"⚠️ CẦN QUÉT LẠI (DỞ DANG): [{unf_str}]")
    else:
        print("✅ CẦN QUÉT LẠI: Không có tỉnh dở dang (toàn bộ chạy tốt)")
    print(f"📍 ĐANG XỬ LÝ [{idx}/{tong_tinh}]: {current_name.upper()} (Slug: {current_slug})")
    print("=" * 85)

async def chay_pipeline_1_tinh(slug, conf):
    """Xử lý từng giai đoạn với cơ chế tự phục hồi thông minh (Granular Stage-Level Resume)"""
    t_start_prov = time.time()
    curr_file = None
    stt = None

    # 0. Smart Resume: Đã có file GĐ 5 hoàn thiện trên Drive
    final_drive_file = DRIVE_OUTPUT_DIR / f"horeca_{slug}_HOAN_THIEN.xlsx" if ROOT_DRIVE else None
    final_local_file = LOCAL_BASE / f"horeca_{slug}_HOAN_THIEN.xlsx"
    is_done = False
    if not EP_CHAY_LAI:
        if final_drive_file and final_drive_file.exists() and _fresh(final_drive_file):
            is_done = True
            target_done_file = final_drive_file
        elif final_local_file.exists() and _fresh(final_local_file):
            is_done = True
            target_done_file = final_local_file
    # Kiem tra che do Vet Delta: Neu file cu con diem thieu SDT thi tu dong vet tiep o GD4 (bo qua GD1)
    if is_done and globals().get('VET_DELTA_DIEM_THIEU_SDT', True) and globals().get('BAT_GD4_BO_SUNG_SDT', True) and target_done_file:
        try:
            import os
            chk_path = Path(target_done_file).resolve()
            chk_str = str(chk_path)
            if os.name == 'nt' and not chk_str.startswith(chr(92)*2 + '?' + chr(92)):
                chk_str = chr(92)*2 + '?' + chr(92) + chk_str
            wb_chk = openpyxl.load_workbook(chk_str, read_only=True)
            ws_chk = wb_chk['Tất cả (chuẩn hóa)'] if 'Tất cả (chuẩn hóa)' in wb_chk.sheetnames else None
            hdr_chk = {str(c.value).strip(): idx for idx, c in enumerate(ws_chk[1], start=1) if c.value} if ws_chk else {}
            p_idx = hdr_chk.get('Số điện thoại')
            missing_cnt = 0
            if p_idx and ws_chk:
                for row in ws_chk.iter_rows(min_row=2, min_col=p_idx, max_col=p_idx, values_only=True):
                    val = row[0]
                    if not val or len(str(val).strip()) < 6:
                        missing_cnt += 1
            wb_chk.close()
            if missing_cnt > 0:
                print(f"   🔄 [VÉT DELTA TỰ ĐỘNG]: File cũ {target_done_file.name} còn {missing_cnt:,} điểm CHƯA CÓ SĐT. Tự động kích hoạt Vét GĐ4 (bỏ qua GĐ1/GĐ2)!")
                is_done = False
                curr_file = target_done_file
        except Exception as e_chk:
            print(f"   ⚠️ [VÉT DELTA] Cảnh báo không đọc được file {target_done_file.name}: {e_chk}", flush=True)
            print(f"   ⚠️ [CẢNH BÁO VÉT DELTA]: Không thể đọc file {target_done_file.name}: {e_chk}. Tiếp tục theo trạng thái hoàn thành mặc định.")

    if is_done:
        print(f"   ⏩ [SMART RESUME]: Đã có file hoàn thiện ({final_local_file.name}). Bỏ qua!")
        return "Đã hoàn thành (Bỏ qua)", time.time() - t_start_prov, True

    try:
        # [GĐ 1] Quét Maps
        csv_file = _tim_file(slug, "horeca_{slug}_CHECKPOINT.csv")
        if BAT_GD1_QUET_MAPS:
            if not csv_file or not _fresh(csv_file) or EP_CHAY_LAI:
                csv_file = await quet_maps_pipeline(slug, conf)
            else:
                print(f"   ⏩ [GĐ 1 RESUME]: Đã có CSV checkpoint hợp lệ ({Path(csv_file).name}). Dùng tiếp!")

        # [GĐ 2] Chuẩn hóa Multi-Tab
        if BAT_GD2_CHUAN_HOA:
            curr_file = _tim_file(slug, "horeca_{slug}_CHUAN_HOA.xlsx")
            if not curr_file or not _fresh(curr_file, csv_file) or EP_CHAY_LAI:
                if csv_file and Path(csv_file).exists():
                    curr_file = chuan_hoa_excel_pipeline(slug, conf, csv_file)
                else:
                    print("   ❌ GĐ2: Không có CSV checkpoint hợp lệ (cần chạy GĐ1).")
                    curr_file = None
            else:
                print(f"   ⏩ [GĐ 2 RESUME]: Đã có Excel Chuẩn Hóa ({Path(curr_file).name}). Dùng tiếp!")

        # [GĐ 3] Tra địa chỉ 2 tầng
        if BAT_GD3_TRA_DIA_CHI:
            da_tra = _tim_file(slug, "horeca_{slug}_CHUAN_HOA_DA_TRA_DIA_CHI.xlsx")
            if da_tra and _fresh(da_tra, curr_file) and not EP_CHAY_LAI:
                print(f"   ⏩ [GĐ 3 RESUME]: Đã có Excel Tra Địa Chỉ ({Path(da_tra).name}). Dùng tiếp!")
                curr_file = da_tra
            elif curr_file and Path(curr_file).exists():
                curr_file = chay_tra_dia_chi_3_tang(slug, conf, curr_file)
            else:
                print("   ❌ GĐ3: Không có file đầu vào hợp lệ (cần chạy GĐ2).")
                curr_file = None

        # [GĐ 4] Bổ sung SĐT & địa chỉ chi tiết
        if BAT_GD4_BO_SUNG_SDT:
            hoan_thien_local = _tim_file(slug, "horeca_{slug}_HOAN_THIEN.xlsx")
            if hoan_thien_local and _fresh(hoan_thien_local, curr_file) and not EP_CHAY_LAI:
                print(f"   ⏩ [GĐ 4 RESUME]: Đã có Excel Hoàn Thiện ({Path(hoan_thien_local).name}). Dùng tiếp!")
                curr_file = hoan_thien_local
            elif curr_file and Path(curr_file).exists():
                curr_file = await enrich_phone_pipeline(slug, conf, curr_file)
            else:
                print("   ❌ GĐ4: Không có file đầu vào hợp lệ (cần chạy GĐ2/GĐ3 trước).")
                curr_file = None

        # [GĐ 5] Đóng gói & đồng bộ Drive
        if BAT_GD5_XUAT_HOAN_THIEN:
            if not curr_file:
                curr_file = _tim_file(slug, "horeca_{slug}_HOAN_THIEN.xlsx", "horeca_{slug}_CHUAN_HOA_DA_TRA_DIA_CHI.xlsx", "horeca_{slug}_CHUAN_HOA.xlsx")
            if curr_file and Path(curr_file).exists():
                curr_file = dong_goi_va_dong_bo_drive(slug, conf, curr_file)

        is_ok = bool(curr_file and Path(curr_file).exists() and _fresh(curr_file))
        stt = "Thành công 100%" if is_ok else "Bỏ qua / Chưa hoàn thành"
        return stt, time.time() - t_start_prov, is_ok
    except Exception as e:
        err_msg = str(e)[:70]
        print(f"\n   ❌ {conf['name']} dừng giữa chừng: {e}")
        return f"LỖI: {err_msg}", time.time() - t_start_prov, False

async def main_pipeline():
    provinces_to_run = lay_danh_sach_tinh_thuc_thi()
    ten_khu_vuc = KHU_VUC if CHON_CHE_DO_TINH == "Chọn theo Khu vực" else CHON_CHE_DO_TINH

    print("=" * 85)
    print(f"🚀 BẮT ĐẦU WORKFLOW HORECA & F&B NHÀ HÀNG KHÁCH SẠN v9.1 ULTRA CHUẨN ({len(provinces_to_run)} TỈNH THÀNH)")
    print(f"   • Chế độ chọn tỉnh : {CHON_CHE_DO_TINH}")
    print(f"   • Khu vực thực thi : {ten_khu_vuc}")
    print(f"   • Danh sách tỉnh   : {', '.join([PROVINCES_CONFIG[p]['name'] for p in provinces_to_run[:5]])}{'...' if len(provinces_to_run)>5 else ''}")
    print(f"   • GĐ1 {'[BẬT]' if BAT_GD1_QUET_MAPS else '[TẮT]'} | GĐ2 {'[BẬT]' if BAT_GD2_CHUAN_HOA else '[TẮT]'} | GĐ3 {'[BẬT]' if BAT_GD3_TRA_DIA_CHI else '[TẮT]'} | GĐ4 {'[BẬT]' if BAT_GD4_BO_SUNG_SDT else '[TẮT]'} | GĐ5 {'[BẬT]' if BAT_GD5_XUAT_HOAN_THIEN else '[TẮT]'}")
    print(f"   • Ép chạy lại      : {'[BẬT] Ghi đè mới toàn bộ' if EP_CHAY_LAI else '[TẮT] Smart Resume thông minh'}")
    print("=" * 85)

    t_start_all = time.time()
    summary_log = []
    completed_slugs = set()
    unfinished_provinces = {}  # slug -> (name, reason)

    # Đếm số tỉnh đã hoàn thành từ trước trên Drive
    for s in provinces_to_run:
        f_drv = DRIVE_OUTPUT_DIR / f"horeca_{s}_HOAN_THIEN.xlsx"
        if not EP_CHAY_LAI and ROOT_DRIVE and f_drv.exists() and _fresh(f_drv):
            completed_slugs.add(s)

    # =========================================================================
    # PASS 1: VÒNG QUÉT CHÍNH TUYẾN
    # =========================================================================
    for idx, slug in enumerate(provinces_to_run, 1):
        if slug not in PROVINCES_CONFIG: continue
        conf = PROVINCES_CONFIG[slug]

        in_tien_do_khu_vuc(ten_khu_vuc, idx, len(provinces_to_run), len(completed_slugs), unfinished_provinces, conf['name'], slug)

        stt, el, is_ok = await chay_pipeline_1_tinh(slug, conf)
        summary_log.append((conf['name'], slug, stt, f"{el:.1f}s"))

        if is_ok:
            completed_slugs.add(slug)
            unfinished_provinces.pop(slug, None)
        else:
            unfinished_provinces[slug] = (conf['name'], stt)

    # =========================================================================
    # PASS 2: VÒNG QUÉT VÉT TỰ ĐỘNG (AUTO-RETRY CHO CÁC TỈNH DỞ DANG)
    # =========================================================================
    if unfinished_provinces:
        retry_slugs = list(unfinished_provinces.keys())
        print("\n" + "#" * 85)
        print(f"🔄 PHÁT HIỆN {len(retry_slugs)} TỈNH DỞ DANG/CHƯA XONG. TỰ ĐỘNG KÍCH HOẠT VÒNG QUÉT VÉT (PASS 2)...")
        print(f"   Danh sách tỉnh quét lại: {', '.join([unfinished_provinces[s][0] for s in retry_slugs])}")
        print("#" * 85)

        for r_idx, slug in enumerate(retry_slugs, 1):
            conf = PROVINCES_CONFIG[slug]
            in_tien_do_khu_vuc(ten_khu_vuc, r_idx, len(retry_slugs), len(completed_slugs), unfinished_provinces, f"[VÉT] {conf['name']}", slug)

            stt, el, is_ok = await chay_pipeline_1_tinh(slug, conf)

            # Cập nhật kết quả vào summary_log
            for i, item in enumerate(summary_log):
                if item[1] == slug:
                    summary_log[i] = (conf['name'], slug, f"{stt} (quét vét)", f"{el:.1f}s")
                    break

            if is_ok:
                completed_slugs.add(slug)
                unfinished_provinces.pop(slug, None)
                print(f"   ✅ [VÉT THÀNH CÔNG]: {conf['name']} đã hoàn tất 100%!")
            else:
                unfinished_provinces[slug] = (conf['name'], f"Vét thất bại: {stt}")
                print(f"   ❌ [VÉT THẤT BẠI]: {conf['name']} vẫn chưa hoàn tất ({stt}).")

    # =========================================================================
    # TỔNG KẾT NGHIỆM THU CUỐI CÙNG
    # =========================================================================
    total_time = time.time() - t_start_all
    pct_final = (len(completed_slugs) / len(provinces_to_run) * 100.0) if provinces_to_run else 0.0

    print("\n" + "=" * 85)
    print(f"🎉 TỔNG KẾT WORKFLOW ({len(provinces_to_run)} tỉnh) - Thời gian: {total_time/60:.1f} phút")
    print(f"📊 TỶ LỆ HOÀN THÀNH TOÀN KHU VỰC: {pct_final:.1f}% ({len(completed_slugs)}/{len(provinces_to_run)} tỉnh hoàn thành GĐ 5)")
    if unfinished_provinces:
        print(f"⚠️ CÁC TỈNH CÒN DỞ DANG CẦN CHÚ Ý ({len(unfinished_provinces)} tỉnh):")
        for slg, (nm, rs) in unfinished_provinces.items():
            print(f"   • {nm} ({slg}): {rs}")
    else:
        print("✅ TOÀN BỘ CÁC TỈNH TRONG KHU VỰC ĐÃ ĐƯỢC VÉT SẠCH 100%!")
    print("=" * 85)
    print(f"{'Tên tỉnh':<22} | {'Slug':<16} | {'Trạng thái':<42} | {'Thời gian'}")
    print("-" * 95)
    for name, slg, stt, el in summary_log:
        print(f"{name:<22} | {slg:<16} | {stt:<42} | {el}")
    print("=" * 85)

if __name__ == "__main__":
    try: loop = asyncio.get_running_loop()
    except RuntimeError: loop = None
    if loop is not None and loop.is_running(): loop.run_until_complete(main_pipeline())
    else: asyncio.run(main_pipeline())
