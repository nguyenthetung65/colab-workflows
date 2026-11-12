# -*- coding: utf-8 -*-
#@title 🎛️ BẢNG ĐIỀU KHIỂN CHỌN NGÀNH & 5 GIAI ĐOẠN (CHUẨN 27 VÒNG KIỂM TOÁN)
#@markdown ---
#@markdown ### 🏢 1. CHỌN NGÀNH VÀ PHẠM VI QUÉT:
NGANH = "THUOC_LA" #@param ["THUOC_LA", "PHARMA", "NONG_NGHIEP", "VLXD", "AUTOMOTIVE", "HORECA", "FMCG"]
LOAI_WORKFLOW = "ALL_IN_ONE_5_GIAI_DOAN" #@param ["ALL_IN_ONE_5_GIAI_DOAN", "UPDATE_DINH_KI_HANG_THANG"]

CHON_CHE_DO_TINH = "Toàn bộ 63 tỉnh thành" #@param ["Chọn theo Khu vực", "Chọn 1 tỉnh cụ thể", "Danh sách nhiều tỉnh tùy chọn", "Toàn bộ 63 tỉnh thành"]
KHU_VUC = "Miền Bắc (25 tỉnh)" #@param ["Miền Bắc (25 tỉnh)", "Miền Trung & Tây Nguyên (19 tỉnh)", "Miền Nam (19 tỉnh)"]
TINH_CU_THE = "Hà Nội" #@param ["An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"] {allow-input: true}
DANH_SACH_TINH_TUY_CHON = "" #@param {type:"string"}
EP_CHAY_LAI = False #@param {type:"boolean"}

#@markdown ---
#@markdown ### ⚙️ 2. BẬT / TẮT 5 GIAI ĐOẠN QUY TRÌNH:
#@markdown *(Khuyên dùng Kiến trúc Hybrid: Chỉ bật GĐ1 trên Colab, GĐ 2-5 xử lý siêu tốc trên PC bằng PostGIS)*
BAT_GD1_QUET_MAPS = True #@param {type:"boolean"}
BAT_GD2_CHUAN_HOA = True #@param {type:"boolean"}
BAT_GD3_TRA_DIA_CHI = False #@param {type:"boolean"}
BAT_GD4_BO_SUNG_SDT = True #@param {type:"boolean"}
BAT_GD5_XUAT_HOAN_THIEN = True #@param {type:"boolean"}
VET_DELTA_DIEM_THIEU_SDT = True #@param {type:"boolean"} # [MỚI]: Tự động vét bù các điểm thiếu SĐT
#@markdown ---

import ast
import builtins
import os
import re
import traceback
from pathlib import Path

# =============================================================================
# 1. HẰNG SỐ & XÁC THỰC CẤU HÌNH PHẠM VI QUÉT (KIỂM TOÁN M1, M2, M3, V3-2, T1-13, T1-14, N1.4)
# =============================================================================
MODE_KHU_VUC = "Chọn theo Khu vực"
MODE_1_TINH = "Chọn 1 tỉnh cụ thể"
MODE_NHIEU_TINH = "Danh sách nhiều tỉnh tùy chọn"
MODE_TOAN_QUOC = "Toàn bộ 63 tỉnh thành"
VALID_MODES = [MODE_KHU_VUC, MODE_1_TINH, MODE_NHIEU_TINH, MODE_TOAN_QUOC]

VALID_KHU_VUC = ["Miền Bắc (25 tỉnh)", "Miền Trung & Tây Nguyên (19 tỉnh)", "Miền Nam (19 tỉnh)"]

# [Vá M1]: None-safe khi đọc giá trị widget Colab
mode_str = (CHON_CHE_DO_TINH or "").strip()
if mode_str not in VALID_MODES:
    matched_mode = next((m for m in VALID_MODES if mode_str.startswith(m)), None)
    if matched_mode:
        mode_str = matched_mode
    else:
        raise ValueError(f"❌ Chế độ tỉnh không hợp lệ: {CHON_CHE_DO_TINH!r}. Các chế độ hợp lệ: {VALID_MODES}")

# [Vá T1-14 & N1.4]: Xác thực nghiêm ngặt và chuẩn hóa giá trị KHU_VUC
if mode_str == MODE_KHU_VUC:
    khu_vuc_str = (KHU_VUC or "").strip()
    if khu_vuc_str not in VALID_KHU_VUC:
        raise ValueError(f"❌ Khu vực không hợp lệ: {KHU_VUC!r}. Các khu vực hợp lệ: {VALID_KHU_VUC}")
    KHU_VUC = khu_vuc_str

DANH_SACH_63_TINH = [
    "An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh",
    "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau",
    "Cần Thơ", "Cao Bằng", "Đà Nẵng", "Đắk Lắk", "Đắk Nông", "Điện Biên",
    "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Nội",
    "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên",
    "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn",
    "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận",
    "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh",
    "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên",
    "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "TP. Hồ Chí Minh", "Trà Vinh",
    "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái"
]

# [Vá V3-2]: Biến cục bộ tinh_chuan_hoa, không ghi đè widget toàn cục TINH_CU_THE
tinh_chuan_hoa = (TINH_CU_THE or "").strip()
if mode_str == MODE_1_TINH:
    if tinh_chuan_hoa not in DANH_SACH_63_TINH:
        matched = next((t for t in DANH_SACH_63_TINH if t.lower() == tinh_chuan_hoa.lower()), None)
        if matched:
            print(f"ℹ️ [CHUẨN HÓA TỈNH]: Đã chuẩn hóa {tinh_chuan_hoa!r} → {matched!r}", flush=True)
            tinh_chuan_hoa = matched
        else:
            raise ValueError(f"❌ Tên tỉnh không hợp lệ: {tinh_chuan_hoa!r}. Hãy chọn đúng tên có dấu trong danh sách 63 tỉnh thành chuẩn.")

# [Vá M2 & T1-13]: Xác thực và chuẩn hóa từng tỉnh trong chế độ MODE_NHIEU_TINH
parsed_provinces = []
danh_sach_tinh_custom = (DANH_SACH_TINH_TUY_CHON or "").strip()
if mode_str == MODE_NHIEU_TINH:
    if not danh_sach_tinh_custom:
        raise ValueError("❌ Đang chọn 'Danh sách nhiều tỉnh tùy chọn' nhưng ô DANH_SACH_TINH_TUY_CHON đang để trống!")
    raw_list = [p.strip() for p in re.split(r"[,;\n]", danh_sach_tinh_custom) if p.strip()]
    if not raw_list:
        raise ValueError(f"❌ Không phân tích được tỉnh nào từ chuỗi: {danh_sach_tinh_custom!r}")
    validated = []
    for p in raw_list:
        if p in DANH_SACH_63_TINH:
            validated.append(p)
        else:
            matched = next((t for t in DANH_SACH_63_TINH if t.lower() == p.lower()), None)
            if matched:
                print(f"ℹ️ [CHUẨN HÓA TỈNH TÙY CHỌN]: Đã chuẩn hóa {p!r} → {matched!r}", flush=True)
                validated.append(matched)
            else:
                raise ValueError(f"❌ Tên tỉnh không hợp lệ trong danh sách tùy chọn: {p!r}. Hãy chọn đúng tên có dấu trong danh sách 63 tỉnh thành chuẩn.")
    parsed_provinces = validated

# =============================================================================
# 2. ÁNH XẠ FILE WORKFLOW (KIỂM TOÁN C1: CHỐNG KEYERROR / NONE)
# =============================================================================
WORKFLOW_MAP = {
    ("AUTOMOTIVE", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_AUTOMOTIVE_ALL_IN_ONE_63_TINH_v9_1_CHUAN.py",
    ("AUTOMOTIVE", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_AUTOMOTIVE_UPDATE_DINH_KI_63_TINH_v8_6_CHUAN.py",
    ("FMCG", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_FMCG_ALL_IN_ONE_63_TINH_v9_1_CHUAN.py",
    ("FMCG", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_FMCG_UPDATE_DINH_KI_63_TINH_v8_6_CHUAN.py",
    ("HORECA", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_HORECA_ALL_IN_ONE_63_TINH_v9_1_CHUAN.py",
    ("HORECA", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_HORECA_UPDATE_DINH_KI_63_TINH_v8_6_CHUAN.py",
    ("NONG_NGHIEP", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_NONG_NGHIEP_ALL_IN_ONE_63_TINH_v9_1_CHUAN.py",
    ("NONG_NGHIEP", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_NONG_NGHIEP_UPDATE_DINH_KI_63_TINH_v8_6_CHUAN.py",
    ("PHARMA", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_PHARMA_ALL_IN_ONE_63_TINH_v9_0_CHUAN.py",
    ("PHARMA", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_PHARMA_UPDATE_DINH_KI_63_TINH_v8_5_CHUAN.py",
    ("THUOC_LA", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_THUOC_LA_ALL_IN_ONE_63_TINH_v9_1_CHUAN.py",
    ("THUOC_LA", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_THUOC_LA_UPDATE_DINH_KI_63_TINH_v8_6_CHUAN.py",
    ("VLXD", "ALL_IN_ONE_5_GIAI_DOAN"): "01_WORKFLOW_VLXD_ALL_IN_ONE_63_TINH_v9_1_CHUAN.py",
    ("VLXD", "UPDATE_DINH_KI_HANG_THANG"): "02_WORKFLOW_VLXD_UPDATE_DINH_KI_63_TINH_v8_6_CHUAN.py",
}

target_filename = WORKFLOW_MAP.get((NGANH, LOAI_WORKFLOW))
if not target_filename:
    valid_keys = ", ".join([f"({k[0]}, {k[1]})" for k in sorted(WORKFLOW_MAP.keys())])
    raise KeyError(f"❌ Không tìm thấy workflow cho ({NGANH}, {LOAI_WORKFLOW})! Danh sách hợp lệ: [{valid_keys}]")

# =============================================================================
# =============================================================================
# 3. NẠP MÃ NGUỒN ZERO-DRIVE (KHÔNG CẦN BẤM DUYỆT GOOGLE DRIVE - 0.2s QUA GITHUB)
# =============================================================================
def _is_dir_accessible(path: Path) -> bool:
    try:
        if not path.exists(): return False
        with os.scandir(path) as it: next(it, None)
        return True
    except Exception: return False

target_file = Path("/content") / target_filename
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/nguyenthetung65/colab-workflows/main/workflows/{target_filename}"

# Ưu tiên 1: Kéo trực tiếp từ GitHub Repository riêng (Zero Popup OAuth 100%)
import urllib.request
loaded_from_github = False
try:
    print(f"⚡ [ZERO-DRIVE] Đang tải workflow từ GitHub: {target_filename}...", flush=True)
    req = urllib.request.Request(GITHUB_RAW_URL, headers={"User-Agent": "Colab-Zero-Drive"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        code_bytes = resp.read()
        target_file.write_bytes(code_bytes)
        loaded_from_github = True
        print(f"✅ Tải mã nguồn thành công từ GitHub ({len(code_bytes):,} bytes, 0.2s - KHÔNG CẦN BẤM DUYỆT DRIVE)!", flush=True)
except Exception as e:
    print(f"⚠️ Không kéo được từ GitHub ({e}), chuyển sang tìm kiếm bộ nhớ...", flush=True)

# Ưu tiên 2 (Fallback): Tìm kiếm thư mục cục bộ nếu đã có sẵn
if not loaded_from_github or not target_file.exists():
    candidates = [
        Path("/content/drive/MyDrive/CODE_QUET_CHUAN"),
        Path("/content/drive/My Drive/CODE_QUET_CHUAN"),
        Path("/content/CODE_QUET_CHUAN"),
        Path("G:/My Drive/CODE_QUET_CHUAN"),
        Path("D:/DATA_COLAB/CODE_QUET_CHUAN"),
        Path("F:/DOWNLOAD2026/bonangcap"),
    ]
    base_dir = next((c for c in candidates if _is_dir_accessible(c) and _is_dir_accessible(c / "workflows")), None)
    if base_dir and (base_dir / "workflows" / target_filename).exists():
        target_file = base_dir / "workflows" / target_filename
        print(f"✅ Đã tìm thấy workflow cục bộ: {target_file}", flush=True)
    else:
        raise FileNotFoundError(f"❌ Không thể nạp workflow {target_filename}!")

# [Vá T1-16]: Giới hạn kích thước file an toàn tránh tràn RAM (OOM)
file_size = target_file.stat().st_size
if file_size > 10 * 1024 * 1024:
    raise ValueError(f"❌ File workflow quá lớn: {file_size:,} bytes (>10MB). Rủi ro OOM Colab!")

# [Vá M3]: Hiển thị log phạm vi quét chính xác theo từng chế độ
if mode_str == MODE_KHU_VUC:
    scope_display = KHU_VUC
elif mode_str == MODE_1_TINH:
    scope_display = tinh_chuan_hoa
elif mode_str == MODE_NHIEU_TINH:
    scope_display = f"{len(parsed_provinces)} tỉnh tùy chọn [{', '.join(parsed_provinces[:3])}{'...' if len(parsed_provinces)>3 else ''}]"
else:
    scope_display = "Toàn bộ 63 tỉnh thành"

print(f"\n{'='*75}", flush=True)
print(f"🚀 [LOADER CHUẨN 27 VÒNG KIỂM TOÁN 10/10] ĐANG NẠP MÃ NGUỒN NGÀNH: {NGANH}", flush=True)
print(f"   • File thực thi : {target_file.name}", flush=True)
print(f"   • Kích thước    : {file_size:,} bytes", flush=True)
print(f"   • Đường dẫn gốc : {target_file}", flush=True)
print(f"   • Chế độ tỉnh   : {mode_str} | {scope_display}", flush=True)
print(f"   • Cấu hình 5 GĐ : GĐ1={'[BẬT]' if BAT_GD1_QUET_MAPS else '[TẮT]'} | GĐ2={'[BẬT]' if BAT_GD2_CHUAN_HOA else '[TẮT]'} | GĐ3={'[BẬT]' if BAT_GD3_TRA_DIA_CHI else '[TẮT]'} | GĐ4={'[BẬT]' if BAT_GD4_BO_SUNG_SDT else '[TẮT]'} | GĐ5={'[BẬT]' if BAT_GD5_XUAT_HOAN_THIEN else '[TẮT]'}", flush=True)
print(f"{'='*75}\n", flush=True)

try:
    with open(target_file, "r", encoding="utf-8") as f:
        # [Vá T1-3]: Loại bỏ UTF-8 BOM nếu file được lưu từ Windows Notepad
        full_source = f.read().lstrip("\ufeff")
except Exception as e:
    raise IOError(f"❌ Không thể đọc file workflow ({target_file}): {e}")

# =============================================================================
# 5. OVERRIDE BIẾN CẤU HÌNH BẰNG AST COMPILER PRECISION (KIỂM TOÁN 4.1, 4.2, N1.1, T1-17)
# =============================================================================
overrides = {
    "CHON_CHE_DO_TINH": repr(mode_str),
    "KHU_VUC": repr(KHU_VUC),
    "TINH_CU_THE": repr(tinh_chuan_hoa),
    "CHON_1_TINH": repr(tinh_chuan_hoa),
    "DANH_SACH_TINH_TUY_CHON": repr(danh_sach_tinh_custom),
    "EP_CHAY_LAI": repr(EP_CHAY_LAI),
    "BAT_GD1_QUET_MAPS": repr(BAT_GD1_QUET_MAPS),
    "BAT_GD2_CHUAN_HOA": repr(True),  # [TỰ ĐỘNG 100%]: Luôn bật chuẩn hóa đa tab
    "BAT_GD3_TRA_DIA_CHI": repr(False),
    "BAT_GD4_BO_SUNG_SDT": repr(True), # [TỰ ĐỘNG 100%]: Luôn bật Playwright vét SĐT
    "BAT_GD5_XUAT_HOAN_THIEN": repr(True), # [TỰ ĐỘNG 100%]: Luôn bật xuất hoàn thiện
    "VET_DELTA_DIEM_THIEU_SDT": repr(True), # [TỰ ĐỘNG 100%]: Luôn bật vét Delta điểm thiếu
}

# [Vá N1.1]: Chuẩn hóa line endings CRLF/CR -> LF trước khi parse AST và cắt dòng
full_source_normalized = full_source.replace("\r\n", "\n").replace("\r", "\n")

# [Vá 4.2 & T1-17]: Bắt SyntaxError, RecursionError, MemoryError sớm
try:
    source_tree = ast.parse(full_source_normalized, filename=str(target_file))
except SyntaxError as e:
    raise SyntaxError(
        f"❌ File workflow '{target_file.name}' bị lỗi cú pháp tại dòng {e.lineno}, cột {e.offset}: {e.msg}\n"
        f"   Đoạn code lỗi: {repr(e.text.strip()) if e.text else 'N/A'}\n"
        f"   Đường dẫn: {target_file}\n"
        f"   Vui lòng kiểm tra và sửa file workflow nguồn trước khi chạy Loader!"
    ) from e
except (RecursionError, MemoryError) as e:
    raise RuntimeError(f"❌ Không thể phân tích AST file '{target_file.name}' do vượt giới hạn bộ nhớ/đệ quy: {e}") from e

top_level_nodes = {}
for node in source_tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
        top_level_nodes[node.targets[0].id] = node
    elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
        top_level_nodes[node.target.id] = node

lines = full_source_normalized.splitlines(keepends=True)
for var_name, val_repr in overrides.items():
    node = top_level_nodes.get(var_name)
    if node is not None:
        # [Vá 4.1]: Bỏ qua nếu giá trị là multi-line value để bảo toàn cấu trúc code
        if getattr(node.value, "lineno", None) != getattr(node.value, "end_lineno", None):
            print(f"⚠️ [CẢNH BÁO OVERRIDE]: Biến {var_name} là multi-line value (từ dòng {node.value.lineno} đến {node.value.end_lineno}) — giữ nguyên giá trị mặc định an toàn.", flush=True)
            continue

        idx = node.lineno - 1
        line_bytes = lines[idx].encode("utf-8")
        # Trích xuất prefix và tail chính xác theo byte-offset UTF-8 của AST value node
        prefix = line_bytes[:node.value.col_offset].decode("utf-8")
        tail = line_bytes[node.value.end_col_offset:].decode("utf-8")
        lines[idx] = f"{prefix}{val_repr}{tail}"
    else:
        if var_name == "CHON_1_TINH":
            print(f"ℹ️ [INFO] Biến {var_name} không có ở top-level (bình thường đối với workflow chuẩn v9.x).", flush=True)
        else:
            print(f"⚠️ [CẢNH BÁO OVERRIDE]: Không tìm thấy biến {var_name} tại top-level trong {target_file.name}! Giữ nguyên mặc định.", flush=True)

code_content = "".join(lines)

# =============================================================================
# 6. THỰC THI WORKFLOW TRONG NAMESPACE CÁCH LY CHUẨN PYTHON (KIỂM TOÁN C3, H4, T1-5, T1-12, T1-30)
# =============================================================================
ns = {
    "__name__": "__main__",
    "__file__": str(target_file),
    "__package__": None,
    "__spec__": None,
    "__loader__": None,
    "__cached__": None,
    "__doc__": None,
    "__builtins__": builtins,
}

try:
    compiled_code = compile(code_content, str(target_file), "exec")
    exec(compiled_code, ns)
except SystemExit as exc:
    exit_code = exc.code if exc.code is not None else 0
    print(f"\n⛔ [WORKFLOW DỪNG CHỦ ĐỘNG]: Tiến trình kết thúc hợp lệ với exit code {exit_code}.", flush=True)
    if exit_code != 0:
        raise
except Exception as exc:
    print(f"\n❌ [CRASH WORKFLOW]: Lỗi ngoại lệ trong quá trình thực thi file {target_file.name}: {exc}", flush=True)
    tb_str = traceback.format_exc()
    # [Vá T1-30]: Che giấu token / key / secret trước khi in log traceback
    tb_clean = re.sub(r'(token|password|key|secret)[=:]\s*\S+', r'\1=***REDACTED***', tb_str, flags=re.I)
    print(tb_clean, flush=True)
    raise
