#!/usr/bin/env python3
"""익명화 **검사** 도구 — 리서처가 익명화한 파일에 남은 PII의 위치를 알려준다.

canonical script for `transcript-anonymizer-skill` (AGENTS.md §4-1).
판정 기준은 `익명화_공통규칙.md`이며, 규칙을 이 파일에 복제하지 않는다.

## 정책 (2026-08-27 사용자 확정)

- **익명화는 리서처가 직접 한다.** 이 스크립트는 치환하지 않고, 어떤 파일도 수정하지 않는다.
- **탐지한 값을 저장하거나 출력하지 않는다.** 마스킹한 형태(`김***님`)도 남기지 않는다 —
  첫 글자와 길이만으로도 좁혀지기 때문이다. 내보내는 것은 **위치(파일·시트·행)와
  카테고리와 건수**뿐이다. 값을 출력하는 모드는 제공하지 않는다.
- **PID 매핑을 제안하지 않는다.** 어떤 이름을 어떤 PID로 바꿀지는 리서처가 결정한다.

## 사용

    python scan_pii.py <파일...>                      # 카테고리별 건수
    python scan_pii.py <파일...> --locate             # 행 단위 위치까지
    python scan_pii.py <파일...> --save-counts out.json   # 건수 집계만 저장

## 가정 (새 데이터에 쓰기 전 확인)

- `.docx`(머리말·꼬리말·주석·각주·메모 포함, SDT 구조 대응) · `.xlsx`/`.xlsm` · `.csv` · `.txt`/`.md`
- `.pdf`·`.xls` 미지원 — 건너뛴 파일은 결과에 명시한다(조용히 넘기지 않는다).
- 한국어 이름 탐지는 `성+이름+호칭` 형태만 잡는다. **호칭 없는 맨 이름·별명은 탐지되지 않는다.**
  따라서 0건이 "PII 없음"을 뜻하지 않는다.
"""
import argparse
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 서비스명·서비스 제공 기업명은 100% 보존 대상 (익명화_공통규칙.md §2)
PRESERVE = [
    "하나은행", "하나카드", "하나증권", "하나금융", "하나원큐", "하나페이", "하나EZ", "원큐",
    "토스", "카카오뱅크", "카카오페이", "케이뱅크", "신한은행", "국민은행", "KB국민", "우리은행",
    "농협", "NH농협", "기업은행", "삼성증권", "미래에셋", "한국투자증권", "키움증권", "네이버페이",
    "삼성페이", "애플페이", "신한카드", "삼성카드", "현대카드", "롯데카드", "BC카드", "제로페이",
    "삼성생명", "한화생명", "교보생명", "동양생명", "신한라이프", "메리츠", "DB손해보험", "KB손해보험",
]

HONORIFIC = r"(?:님|씨|선생님|학생|매니저|과장|차장|부장|팀장|대리|사원|주임|실장|이사|대표)"

PATTERNS = {
    "name_with_honorific": re.compile(
        r"(?<![가-힣])[김이박최정강조윤장임한오서신권황안송류전홍고문양손배백허유남심노정하곽성차주우구민진지엄채원천방공강현함변염여추도소석선설마길연위표명기반라왕금옥육인맹제모탁국여진성]"
        r"[가-힣]{1,2}\s?" + HONORIFIC),
    "mobile_phone":     re.compile(r"01[016789][-\s.]?\d{3,4}[-\s.]?\d{4}"),
    "landline_phone":   re.compile(r"\b0\d{1,2}[-\s.]\d{3,4}[-\s.]\d{4}\b"),
    "email":            re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}"),
    "rrn":              re.compile(r"\b\d{6}\s?[-–]\s?[1-4]\d{6}\b"),
    "card_or_account":  re.compile(r"\b\d{3,6}[-\s]\d{2,6}[-\s]\d{2,6}(?:[-\s]\d{2,6})?\b"),
    "school":           re.compile(r"[가-힣A-Za-z]{2,10}(?:대학교|대학원|고등학교|중학교|초등학교)"),
    "company":          re.compile(
        r"(?:\(주\)\s?[가-힣A-Za-z]{2,12}"
        r"|[가-힣]{2,10}(?:전자|화학|건설|물산|생명|손해보험|보험|캐피탈|텔레콤|중공업|제철)"
        r"|[가-힣A-Za-z]{2,12}\s?(?:주식회사))"),
    "address":          re.compile(
        r"(?:서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)"
        r"\s?(?:특별시|광역시|도)?\s?[가-힣]{2,10}(?:시|군|구)\s?[가-힣0-9]{1,12}(?:동|읍|면|로|길)"),
    "researcher_intro": re.compile(r"(?:저는|제가)\s?[가-힣]{2,4}\s?(?:입니다|이라고|라고)"),
}

# 성씨처럼 시작하지만 실제로는 직함·일반명사 (익명화_공통규칙.md §5)
# 실측: 이름 후보 631건 중 393건이 이 부류, `선생님` 단독이 346건.
COMMON_NOUN_HONORIFIC = {
    "선생님", "고객님", "차장님", "소장님", "박사님", "원장님", "이사님", "기사님", "여사님",
    "실장님", "사모님", "부장님", "과장님", "팀장님", "사장님", "대리님", "주임님", "반장님",
    "조장님", "감독님", "목사님", "신부님", "수녀님", "교수님", "강사님", "회장님", "국장님",
    "형님", "누님", "아드님", "따님", "어머님", "아버님", "주인님", "도련님", "영감님", "며느님",
    "신입사원", "기존사원", "담당사원", "정규사원", "계약사원", "승무원", "상담원", "안내원",
}

# 회사명이 아니라 제도·상품 이름 (실측 100건 오탐)
NOT_A_COMPANY = re.compile(
    r"^(?:건강|사대|고용|산재|연금|사회|의료|장기요양|실손|자동차|화재|여행자|암|종신|정기|저축|변액|연금저축|퇴직연금)"
    r"(?:보험|저축보험)$|보험료$|보험공단$")

# 날짜·시각은 계좌·카드번호가 아니다 (실측 81건 오탐)
DATE_LIKE = re.compile(r"^\s*(?:19|20)\d{2}\s?[-.\s/]\s?\d{1,2}\s?[-.\s/]\s?\d{1,2}")

# 이미 익명화된 화자 라벨 (익명화_공통규칙.md §4 — 손대지 않는다)
ANON_LABEL = re.compile(r"^(?:\[)?(?:P|S|UX|R)\d{1,3}(?:\])?$|^참여자\s?\d*$|^(?:진행자|모더레이터|사회자|연구원)$")
SPEAKER_LINE = re.compile(r"^\s*(?:\[)?([^\s:：\]]{1,12})(?:\])?\s*[:：]")

SUPPORTED = {".docx", ".xlsx", ".xlsm", ".csv", ".txt", ".md"}


# --------------------------------------------------------------- 읽기

def read_docx(p):
    """본문 + 머리말·꼬리말·주석·각주·메모. SDT 구조 대응으로 raw XML을 긁는다."""
    z = zipfile.ZipFile(p)
    out = []
    for name in z.namelist():
        if re.match(r"word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml$", name):
            part = re.sub(r"^word/|\.xml$", "", name)
            x = z.read(name).decode("utf-8", "ignore")
            for i, para in enumerate(re.split(r"</w:p>", x), 1):
                ts = re.findall(r"<w:t(?:\s[^>]*)?>(.*?)</w:t>", para, re.S)
                t = "".join(ts).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
                if t.strip():
                    out.append((part, i, t.strip()))
    return out


def read_xlsx(p):
    import openpyxl
    wb = openpyxl.load_workbook(p, data_only=True)
    out = []
    for ws in wb.worksheets:
        for r, row in enumerate(ws.iter_rows(values_only=True), 1):
            for c in row:
                if c is None:
                    continue
                s = str(c).strip()
                if s:
                    out.append((ws.title, r, s))
    return out


def read_plain(p):
    lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    return [("(text)", i, ln.strip()) for i, ln in enumerate(lines, 1) if ln.strip()]


def read_csv(p):
    import csv as _csv
    out = []
    with open(p, encoding="utf-8-sig", newline="") as f:
        for r, row in enumerate(_csv.reader(f), 1):
            for cell in row:
                if cell and cell.strip():
                    out.append(("(csv)", r, cell.strip()))
    return out


def read_any(p):
    ext = p.suffix.lower()
    if ext == ".docx":
        return read_docx(p)
    if ext in (".xlsx", ".xlsm"):
        return read_xlsx(p)
    if ext == ".csv":
        return read_csv(p)
    return read_plain(p)


# --------------------------------------------------------------- 검사

def scan(path):
    """값을 담지 않는다. 카테고리·건수·위치만 돌려준다."""
    p = Path(path)
    if p.suffix.lower() not in SUPPORTED:
        return {"file": p.name, "skipped": "미지원 확장자(%s) — 검사하지 못했다" % p.suffix}
    try:
        units = read_any(p)
    except Exception as e:
        return {"file": p.name, "skipped": "읽기 실패(%s)" % type(e).__name__}

    counts = Counter()
    dropped = Counter()
    preserved = 0
    locations = defaultdict(list)        # category -> [(sheet, row), ...]
    anon_labels = set()
    other_labels = set()

    for sheet, row, text in units:
        m = SPEAKER_LINE.match(text)
        if m:
            lab = m.group(1).strip()
            (anon_labels if ANON_LABEL.match(lab) else other_labels).add((sheet, lab))
        for cat, rx in PATTERNS.items():
            for mt in rx.finditer(text):
                v = mt.group(0)
                if any(w in v for w in PRESERVE):
                    preserved += 1
                    continue
                if cat == "name_with_honorific" and v.strip().replace(" ", "") in COMMON_NOUN_HONORIFIC:
                    dropped["name_is_a_common_noun"] += 1
                    continue
                if cat == "company" and NOT_A_COMPANY.search(v.strip()):
                    dropped["company_is_a_scheme_name"] += 1
                    continue
                if cat == "card_or_account" and DATE_LIKE.match(v):
                    dropped["card_is_a_date"] += 1
                    continue
                counts[cat] += 1
                if len(locations[cat]) < 200:
                    locations[cat].append((sheet, row))

    return {
        "file": p.name,
        "units": len(units),
        "counts": dict(sorted(counts.items())),
        "locations": {k: v for k, v in locations.items()},
        "preserved_service_name_matches": preserved,
        "dropped_false_positives": dict(dropped),
        "already_anonymized_labels": len(anon_labels),
        "other_speaker_labels": len(other_labels),
    }


# --------------------------------------------------------------- 보고

def report(results, locate=False):
    total = Counter()
    files_with = files_clean = skipped = 0
    for r in results:
        if r.get("skipped"):
            skipped += 1
            print("SKIP  %s — %s" % (r["file"], r["skipped"]))
            continue
        if r["counts"]:
            files_with += 1
        else:
            files_clean += 1
        for k, v in r["counts"].items():
            total[k] += v

    print()
    print("검사 파일 %d개 | 잔존 후보 있음 %d | 없음 %d | 검사 못함 %d"
          % (len(results), files_with, files_clean, skipped))
    print()
    if total:
        print("카테고리별 잔존 건수:")
        for k, v in total.most_common():
            print("   %5d  %s" % (v, k))
    else:
        print("잔존 후보 0건.")
    print()

    for r in results:
        if r.get("skipped") or not r["counts"]:
            continue
        print("── %s" % r["file"])
        for cat, n in sorted(r["counts"].items(), key=lambda x: -x[1]):
            line = "     %-20s %4d건" % (cat, n)
            if locate:
                locs = r["locations"].get(cat, [])
                shown = ", ".join("%s:%d" % (s, row) for s, row in locs[:12])
                more = "" if len(locs) <= 12 else " … 외 %d곳" % (len(locs) - 12)
                line += "   위치 → %s%s" % (shown, more)
            print(line)
        if r["preserved_service_name_matches"]:
            print("     (보존 확인: 서비스명 %d건 — 지워지지 않았다)"
                  % r["preserved_service_name_matches"])
        if r["already_anonymized_labels"]:
            print("     (이미 익명화된 화자 라벨 %d종 — 손대지 않아도 된다)"
                  % r["already_anonymized_labels"])
        if r["dropped_false_positives"]:
            print("     (오탐 제외: %s)" % r["dropped_false_positives"])

    clean = [r for r in results if not r.get("skipped") and not r["counts"]]
    if clean:
        print()
        print("잔존 후보 0건인 파일:")
        for r in clean:
            extra = []
            if r["already_anonymized_labels"]:
                extra.append("이미 익명화된 화자 라벨 %d종" % r["already_anonymized_labels"])
            if r["preserved_service_name_matches"]:
                extra.append("서비스명 %d건 보존" % r["preserved_service_name_matches"])
            print("     %s%s" % (r["file"], ("  (%s)" % " · ".join(extra)) if extra else ""))

    print()
    print("※ 값은 출력하지 않는다. 위치를 열어 직접 확인·수정할 것 (익명화_공통규칙.md).")
    print("※ 호칭 없는 맨 이름·별명은 이 방식으로 탐지되지 않는다 — 0건이 'PII 없음'을 뜻하지 않는다.")
    if not locate:
        print("※ 행 단위 위치가 필요하면 --locate 를 붙일 것.")
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--locate", action="store_true", help="행 단위 위치까지 출력(값은 없음)")
    ap.add_argument("--save-counts", help="건수 집계만 JSON으로 저장(값·위치 없음)")
    a = ap.parse_args()

    results = [scan(p) for p in a.paths]
    total = report(results, a.locate)

    if a.save_counts:
        slim = [{k: v for k, v in r.items() if k != "locations"} for r in results]
        json.dump({
            "policy": "탐지한 PII 값은 저장하지 않는다(2026-08-27 사용자 확정). 카테고리·건수만.",
            "total": dict(total),
            "files": slim,
        }, open(a.save_counts, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("건수 집계 저장: %s (값·위치 없음)" % a.save_counts)


if __name__ == "__main__":
    main()
