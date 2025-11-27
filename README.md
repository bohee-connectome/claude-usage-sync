# Claude Usage Tracker

> **Created by Bohee Lee** | [English Version](./README_EN.md)

멀티 디바이스 Claude Code 사용량을 Git으로 통합 관리하는 **누적 추적 시스템**입니다.

## 🎯 핵심 특징

✅ **영구 보존**: `.jsonl` 파일이 삭제되어도 토큰 사용량은 계속 누적
✅ **멀티 디바이스**: 맥북, Windows PC 등 모든 기기 합산
✅ **실시간 웹**: GitHub Pages에서 언제 어디서나 조회
✅ **자동 동기화**: Git으로 백업 및 기기 간 통합

## 🌐 웹사이트

**전체 사용량을 브라우저에서 확인하세요:**

👉 **https://bohee-connectome.github.io/claude-usage-sync**

- ✅ 실시간 데이터 조회 (GitHub에서 직접 가져오기)
- ✅ 5분마다 자동 갱신 + 수동 새로고침
- ✅ 모든 기기 합산 통계
- ✅ 100M 토큰 목표 진행률
- ✅ 로그인 불필요, 완전 무료

---

## 📊 명령어

| 명령어 | 기능 | 사용 시기 |
|--------|------|----------|
| **`ccusage`** | 현재 PC 누적 사용량 확인 | 수시로 |
| **`ccusage-sync`** | Git에 동기화 (백업) | 주 1회 or 작업 후 |
| **`ccusage-total`** | 모든 PC 합산 확인 | 월말 확인 |
| **`ccusage-goal`** | 100M 토큰 목표 진행률 | 목표 추적 시 |
| **[웹사이트](https://bohee-connectome.github.io/claude-usage-sync)** | 실시간 웹 조회 | 언제든 |

### 💰 ccusage 주요 출력 정보

`ccusage` 실행 시 다음 정보가 표시됩니다:
- **📊 CUMULATIVE TOTAL SESSIONS**: 총 세션 수
- **💰 TOTAL PROCESSED**: Input + Output + Cache Creation 합계 (100M 목표 기준)
- **🔢 CUMULATIVE TOKEN TOTALS**: 토큰 종류별 상세 사용량
- **💵 ESTIMATED COST**: 예상 비용 (Sonnet 4.5 기준)

**💰 TOTAL PROCESSED**는 웹 대시보드와 동일한 수치로, 100M 토큰 목표 달성에 카운트되는 숫자입니다.

---

## 💡 누적 추적 시스템이란?

### 기존 문제점
Claude Code가 오래된 세션 파일(`.jsonl`)을 자동 삭제하면 **토큰 사용 기록이 영구 소실**되었습니다.

### 해결 방법
**누적 데이터베이스**(`~/.claude/cumulative_usage.json`)에 모든 세션을 영구 저장:
- 한 번 카운트된 세션은 고유 ID로 추적
- 파일이 삭제되어도 누적 카운트 유지
- **절대 감소하지 않음!**

### 동작 원리
```
1. .jsonl 파일 스캔
2. 각 세션의 고유 ID 생성 (파일명 + 타임스탬프 + 토큰)
3. 데이터베이스에 이미 있는지 확인
4. 새 세션만 누적 카운트에 추가
5. 영구 데이터베이스 업데이트
```

---

## 🚀 설정 가이드

### 🍎 맥북 설정

```bash
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. Alias 설정
cat >> ~/.zshrc << 'ALIASES'
alias ccusage='python3 ~/claude-usage-tracker/scripts/ccusage_cumulative.py'
alias ccusage-sync='python3 ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python3 ~/claude-usage-tracker/scripts/ccusage_total.py'
alias ccusage-goal='python3 ~/claude-usage-tracker/scripts/ccusage_goal.py'
ALIASES
source ~/.zshrc

# 3. Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 4. 첫 실행
ccusage        # 누적 사용량 확인
ccusage-sync   # Git에 동기화
```

### 🪟 Windows PC 설정

**PowerShell 사용:**

```powershell
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. PowerShell Profile에 Alias 추가
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
Add-Content $PROFILE @"
function ccusage { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_cumulative.py }
function ccusage-sync { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_sync.py }
function ccusage-total { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_total.py }
function ccusage-goal { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_goal.py }
"@

# 3. PowerShell 재시작 후 Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 4. 첫 실행
ccusage        # 누적 사용량 확인
ccusage-sync   # Git에 동기화
```

---

## 📖 사용 방법

### 일상 사용

```powershell
# 현재 누적 사용량 확인
ccusage

# Git에 백업 (주 1회 권장)
ccusage-sync

# 100M 목표 진행률 확인
ccusage-goal
```

### 월말 확인

```powershell
# 모든 기기 합산
ccusage-total

# 또는 웹사이트에서
# https://bohee-connectome.github.io/claude-usage-sync
```

---

## 📁 저장소 구조

```
claude-usage-tracker/
├── README.md                      # 이 파일
├── index.html                     # GitHub Pages 웹사이트
├── create_index.py                # 웹사이트 생성기
├── setup_auto_sync.ps1            # 자동 sync 설정 (Windows)
├── scripts/
│   ├── ccusage_cumulative.py      # 누적 사용량 확인 (메인)
│   ├── ccusage_sync.py            # Git 동기화
│   ├── ccusage_total.py           # 전체 합산
│   ├── ccusage_goal.py            # 100M 목표 추적
│   └── auto_sync.py               # 자동 동기화 (선택)
└── data/
    ├── yangpyungpc.json           # Windows PC 데이터
    └── bohees-macbook-air-local.json  # 맥북 데이터
```

---

## 🎁 다른 사람이 사용하기

### 1️⃣ 리포지토리 Fork

GitHub에서 이 리포지토리를 **Fork**하세요.

### 2️⃣ index.html 수정

`index.html` 파일의 **9번째 줄** 수정:

```javascript
const GITHUB_REPO = 'your-username/your-repo-name';  // 본인 것으로 변경
```

### 3️⃣ GitHub Pages 활성화

1. Settings → Pages
2. Source: `main` branch, `/ (root)`
3. Save

### 4️⃣ 각 디바이스에 설치

위의 "설정 가이드"를 따라 본인 리포지토리를 클론하세요.

---

## 🔧 트러블슈팅

### Q: 세션 수가 감소했어요
**A**: `ccusage`는 누적 추적이므로 **절대 감소하지 않습니다**.
    `.jsonl` 파일이 삭제되어도 누적 DB에 영구 보존됩니다.

### Q: yangpyungpc 업데이트가 안돼요
**A**: `ccusage-sync`를 실행해야 Git에 반영됩니다:
```powershell
ccusage-sync
```

### Q: Git push 실패
**A**: 인증 확인:
```bash
gh auth status
gh auth login
```

### Q: Python 없음
**A**: Python 설치:
```bash
# Windows
winget install Python.Python.3.12

# macOS
brew install python3
```

### Q: 데이터베이스 백업하고 싶어요
**A**: 누적 DB 백업:
```powershell
# Windows
Copy-Item "$env:USERPROFILE\.claude\cumulative_usage.json" `
          "~\Desktop\cumulative_backup_$(Get-Date -Format 'yyyyMMdd').json"

# macOS
cp ~/.claude/cumulative_usage.json ~/Desktop/cumulative_backup_$(date +%Y%m%d).json
```

---

## ⚠️ 중요 사항

### ✅ 해야 할 것
1. **정기적으로 `ccusage-sync` 실행** (주 1회 권장)
2. **누적 DB 백업** (`~/.claude/cumulative_usage.json`)
3. **절대 누적 DB 직접 수정하지 않기**

### 📊 12월 31일까지 1억 토큰 목표
```powershell
ccusage-goal  # 목표 진행률 확인
```

---

## 👤 Credits

**Created & Directed by [Bohee Lee](https://github.com/bohee-connectome)**

Built with [Claude Code](https://claude.ai/code) 🤖

**목표: 12월 31일까지 1억 토큰!** 🎯

---

© 2025 Bohee Lee | [English Version](./README_EN.md)
