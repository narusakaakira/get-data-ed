# """
# ed_config.py - cấu hình tách khỏi code: đọc .env, chọn khóa học, khai báo bài cần lấy.

# Thứ tự ưu tiên:  tham số dòng lệnh  >  biến môi trường / .env  >  hỏi trực tiếp (chỉ chọn khóa)

# .env (xem .env.example):
#     ED_USERNAME / ED_PASS        tài khoản (bí mật - không đưa lên git)
#     ED_HOME_URL                  trang chủ
#     ED_PROGRESS_URL              mẫu URL My Progress, có {id}
#     ED_COURSE_<KHÓA>=<id>        khai báo khóa: ED_COURSE_I2=45178, ED_COURSE_I3=45441 (thêm khóa mới = thêm 1 dòng)
#     ED_COURSE                    khóa mặc định (I2 / I3 / để trống = hỏi)
#     ED_TARGETS                   bài cần lấy (để trống = chế độ thủ công, tự gõ nhãn)
#     ED_DELAY                     giây nghỉ giữa các thao tác (mặc định 3)

# Cú pháp ED_TARGETS (nhiều mục cách nhau bởi dấu phẩy hoặc chấm phẩy):
#     ALL                  mọi bài của khóa đã chọn
#     U02                  cả Unit 2             U02..U04        Unit 2 đến 4
#     U02-L03              Unit 2, Lesson 3      U02-L01..L03    Lesson 1 đến 3 của Unit 2
#     I2-U02-L02-Cliff Terror    có thể thêm tiền tố khóa (I2-) và tên bài ở cuối (tên chỉ để dễ đọc/đối chiếu)
# Số unit/lesson là thứ tự HIỂN THỊ trên web (1, 2, 3...), không phải trường Sequence trong dữ liệu.

# Tham số dòng lệnh:   --course I3   (hoặc kiểu cũ --I2 / --I3)   --targets "U02-L01..L03"   --manual
# """
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

ENV_FILE = Path(__file__).with_name(".env")
TARGET_RE = re.compile(
    r"^(?:(?P<course>[A-Za-z]+\d+)-)?"
    r"U(?P<u1>\d+)(?:\.\.U?(?P<u2>\d+))?"
    r"(?:-L(?P<l1>\d+)(?:\.\.L?(?P<l2>\d+))?)?"
    r"(?:-(?P<name>.+))?$", re.I)


# ---------- .env ----------
def load_env(path: Path = ENV_FILE, override: bool = False) -> dict:
    """Đọc KEY=VALUE. Bỏ dòng trống/#, bỏ nháy, bỏ chú thích đuôi ' # ...'. Hỗ trợ BOM của Notepad."""
    vals = {}
    if not path.exists():
        return vals
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        q = re.match(r"""^(["'])(.*?)\1\s*(?:#.*)?$""", v)  # "giá trị có # bên trong"   # chú thích
        if q:
            v = q.group(2)
        else:
            v = re.split(r"\s+#", v, maxsplit=1)[0].strip()
        vals[k] = v
        if override or k not in os.environ:  # ps1 / PowerShell đã nạp thì giữ nguyên
            os.environ[k] = v
    return vals


# ---------- khóa học ----------
def course_map(env=None) -> dict:
    env = os.environ if env is None else env
    out = {}
    for k, v in env.items():
        m = re.fullmatch(r"ED_COURSE_([A-Za-z0-9]+)", k)
        if m and v.strip().isdigit():
            out[m.group(1).upper()] = int(v.strip())
    return out


def cli_value(argv: List[str], flag: str) -> Optional[str]:
    """--flag value  hoặc  --flag=value"""
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return None


def choose_course(argv: List[str], courses: dict, interactive: bool = True) -> Optional[str]:
    """CLI (--course X hoặc --X) > ED_COURSE > hỏi trực tiếp > None (ở lại trang chủ)."""
    key = cli_value(argv, "--course")
    if key is None:  # kiểu cũ: --I2 / --I3 (bất kỳ khóa nào đã khai báo)
        key = next((a.lstrip("-") for a in argv if a.startswith("--") and a.lstrip("-").upper() in courses), None)
    if key is None:
        key = os.environ.get("ED_COURSE", "")
    key = key.strip().upper()
    if key in ("NONE", "-"):
        return None
    if not key:
        if interactive and sys.stdin.isatty() and courses:
            opts = "/".join(sorted(courses))
            key = input(f"Chọn khóa [{opts}] (Enter = ở lại trang chủ): ").strip().upper()
        if not key:
            return None
    if key not in courses:
        raise SystemExit(f"Khóa '{key}' chưa khai báo. Đã có: {', '.join(sorted(courses)) or '(chưa có)'}. "
                         f"Thêm dòng ED_COURSE_{key}=<id> vào .env")
    return key


# ---------- bài cần lấy ----------
@dataclass
class Target:
    course: Optional[str]
    u1: int
    u2: int
    l1: Optional[int]  # None = mọi lesson của unit
    l2: Optional[int]
    name: str = ""

    def matches(self, course: str, unit: int, lesson: int) -> bool:
        if self.course and self.course.upper() != course.upper():
            return False
        if not (self.u1 <= unit <= self.u2):
            return False
        return self.l1 is None or (self.l1 <= lesson <= (self.l2 or self.l1))


def parse_targets(text: str) -> List[Target]:
    """'' -> [] (thủ công); 'ALL' -> [Target mọi unit]; còn lại theo cú pháp ở đầu file."""
    out = []
    for item in re.split(r"[;,]", text or ""):
        item = item.strip()
        if not item:
            continue
        if item.upper() in ("ALL", "*"):
            out.append(Target(None, 1, 10 ** 6, None, None))
            continue
        m = TARGET_RE.match(item)
        if not m:
            raise SystemExit(f"Không hiểu mục bài '{item}'. Ví dụ đúng: U02, U02-L03, U02-L01..L03, ALL")
        u1 = int(m["u1"]); u2 = int(m["u2"] or u1)
        l1 = int(m["l1"]) if m["l1"] else None
        l2 = int(m["l2"] or m["l1"]) if m["l1"] else None
        if u2 < u1 or (l1 and l2 < l1):
            raise SystemExit(f"Khoảng bị ngược trong '{item}'")
        out.append(Target(m["course"], u1, u2, l1, l2, m["name"] or ""))
    return out


def wanted(targets: List[Target], course: str, unit: int, lesson: int) -> bool:
    return any(t.matches(course, unit, lesson) for t in targets)


def make_label(course: str, unit: int, lesson: int, name: str) -> str:
    """Nhãn thư mục: I2-U02-L01-Be Careful  (tên được chuẩn hóa khoảng trắng thừa)."""
    clean = re.sub(r"\s+", " ", name).strip()
    return f"{course}-U{unit:02d}-L{lesson:02d}-{clean}"


# ---------- gộp lại ----------
@dataclass
class Settings:
    username: str
    password: str
    home_url: str
    progress_url: str
    courses: dict
    course: Optional[str]
    targets: List[Target]
    delay: float

    @property
    def mode(self) -> str:
        return "auto" if self.targets else "manual"

    def course_url(self, key: Optional[str] = None) -> Optional[str]:
        key = key or self.course
        return self.progress_url.format(id=self.courses[key]) if key else None

    def describe(self) -> str:
        u = self.username
        masked = (u[:2] + "***" + u[-2:]) if len(u) > 4 else ("***" if u else "(trống)")
        return (f"[cấu hình] tài khoản={masked} | khóa={self.course or 'ở trang chủ'} "
                f"| bài={'tự động ' + str(len(self.targets)) + ' mục' if self.targets else 'thủ công (tự gõ nhãn)'} "
                f"| nghỉ={self.delay}s")


def load_settings(argv: Optional[List[str]] = None, interactive: bool = True) -> Settings:
    argv = sys.argv[1:] if argv is None else argv
    load_env()
    courses = course_map()
    known = {"--course", "--targets", "--manual", "--dry-run", "--redo"}
    for a in argv:  # gõ nhầm tham số thì báo, không im lặng bỏ qua
        if a.startswith("--") and a.split("=", 1)[0] not in known and a.lstrip("-").upper() not in courses:
            print(f"[cảnh báo] bỏ qua tham số lạ: {a}")
    course = choose_course(argv, courses, interactive)
    if "--manual" in argv:
        targets = []
    else:
        targets = parse_targets(cli_value(argv, "--targets") if cli_value(argv, "--targets") is not None
                                else os.environ.get("ED_TARGETS", ""))
    if targets and not course:
        raise SystemExit("Có khai báo bài cần lấy nhưng chưa chọn khóa (--course hoặc ED_COURSE).")
    try:
        delay = float(os.environ.get("ED_DELAY", "3"))
    except ValueError:
        delay = 3.0
    return Settings(
        username=os.environ.get("ED_USERNAME", ""),
        password=os.environ.get("ED_PASS", ""),
        home_url=os.environ.get("ED_HOME_URL", "https://ed22.engdis.com/ptithcm#/home"),
        progress_url=os.environ.get("ED_PROGRESS_URL", "https://ed22.engdis.com/ptithcm#/MyProgress/Course/{id}/Unit/"),
        courses=courses, course=course, targets=targets, delay=delay)


if __name__ == "__main__":  # kiểm tra nhanh:  python ed_config.py --course I3 --targets "U02-L01..L03"
    s = load_settings()
    print(s.describe())
    print("URL khóa:", s.course_url())
    for t in s.targets:
        print("  mục:", t)
