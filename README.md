# Claude Usage Tracker

멀티 디바이스 Claude Code 사용량을 Git으로 통합 관리하는 시스템입니다.

## 🌐 웹사이트

**전체 사용량을 브라우저에서 확인하세요:**

👉 **https://bohee-connectome.github.io/claude-usage-sync**

- ✅ **실시간 데이터 조회** - GitHub에서 직접 최신 데이터 가져오기
- ✅ **자동 갱신** - 5분마다 자동 업데이트 (수동 새로고침도 가능)
- ✅ **캐시 없음** - `ccusage-sync` 실행 후 즉시 반영
- ✅ **모든 기기 합산** - 전체 통계 한눈에 확인
- ✅ **반응형 디자인** - 모바일/태블릿 지원
- ✅ **로그인 불필요** - 어디서든 접속 가능
- ✅ **완전 무료** - GitHub Pages 호스팅

## 🎯 시스템 개요

각 컴퓨터(맥북, Windows PC 등)에서 로컬 Claude Code 사용량을 자동으로 Git 저장소에 동기화하고, 모든 기기의 사용량을 합산해서 확인할 수 있습니다.

```
맥북 A ──┐
맥북 B ──┼─→ Git Repo ─→ 전체 사용량 합산
윈도우 PC ─┘
```

## 📊 사용 명령어

| 방법 | 범위 | 설명 |
|------|------|------|
| **[웹사이트](https://bohee-connectome.github.io/claude-usage-sync)** | 모든 컴퓨터 합산 | 브라우저에서 실시간 조회 (어디서든) |
| `ccusage` | 현재 컴퓨터만 | 터미널에서 로컬 사용량 확인 |
| `ccusage-sync` | 현재 컴퓨터 → Git | 로컬 사용량을 Git에 업로드 |
| `ccusage-total` | 모든 컴퓨터 합산 | 터미널에서 전체 사용량 표시 |

## 🚀 맥북 설정

```bash
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. 설정 파일
mkdir -p ~/.claude
cat > ~/.claude/usage_sync_config.json << 'CONFIG'
{
  "repo_path": "$HOME/claude-usage-tracker",
  "data_dir": "$HOME/claude-usage-tracker/data"
}
CONFIG

# 3. Alias 설정
cat >> ~/.zshrc << 'ALIASES'
alias ccusage='python3 ~/claude-usage-tracker/scripts/calculate_usage.py'
alias ccusage-sync='python3 ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python3 ~/claude-usage-tracker/scripts/ccusage_total.py'
ALIASES
source ~/.zshrc

# 4. Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. 첫 Sync
ccusage-sync
```

## 🪟 Windows PC 설정

**Git Bash 사용 (추천):**

```bash
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. 설정 파일
mkdir -p ~/.claude
cat > ~/.claude/usage_sync_config.json << 'CONFIG'
{
  "repo_path": "$HOME/claude-usage-tracker",
  "data_dir": "$HOME/claude-usage-tracker/data"
}
CONFIG

# 3. Alias 설정
cat >> ~/.bashrc << 'ALIASES'
alias ccusage='python ~/claude-usage-tracker/scripts/calculate_usage.py'
alias ccusage-sync='python ~/claude-usage-tracker/scripts/ccusage_sync.py'
alias ccusage-total='python ~/claude-usage-tracker/scripts/ccusage_total.py'
ALIASES
source ~/.bashrc

# 4. Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. 첫 Sync
ccusage-sync
```

**PowerShell 사용:**

```powershell
# 1. 저장소 클론
cd ~
gh repo clone bohee-connectome/claude-usage-sync claude-usage-tracker

# 2. 설정 파일
mkdir -Force $env:USERPROFILE\.claude
@"
{
  "repo_path": "$env:USERPROFILE\\claude-usage-tracker",
  "data_dir": "$env:USERPROFILE\\claude-usage-tracker\\data"
}
"@ | Out-File -FilePath $env:USERPROFILE\.claude\usage_sync_config.json -Encoding UTF8

# 3. Alias 설정
if (!(Test-Path -Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
Add-Content $PROFILE @"
function ccusage { python `$env:USERPROFILE\claude-usage-tracker\scripts\calculate_usage.py }
function ccusage-sync { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_sync.py }
function ccusage-total { python `$env:USERPROFILE\claude-usage-tracker\scripts\ccusage_total.py }
"@

# 4. PowerShell 재시작 후 Git 설정
cd ~/claude-usage-tracker
git config user.email "claude-usage@local.dev"
git config user.name "Claude Usage Tracker"

# 5. 첫 Sync
ccusage-sync
```

## 📖 사용 방법

**로컬만 확인:**
```bash
ccusage
```

**주간 업로드 (매주 월요일):**
```bash
ccusage-sync
```

**월말 전체 확인:**
```bash
ccusage-total
```

## 📁 저장소 구조

```
claude-usage-tracker/
├── README.md
├── index.html              # GitHub Pages 웹사이트
├── scripts/
│   ├── calculate_usage.py   # 로컬 사용량 계산
│   ├── export_usage.py      # JSON export
│   ├── ccusage_sync.py      # Git sync
│   └── ccusage_total.py     # 전체 합산
└── data/
    ├── macbook.json
    ├── windows-pc.json
    └── ...
```

## 🎁 다른 사람이 사용하기

이 프로젝트를 본인의 GitHub 계정에서 사용하려면:

### 1️⃣ 리포지토리 복사

**방법 A: Fork (추천)**
1. 이 리포지토리의 GitHub 페이지에서 "Fork" 버튼 클릭
2. 본인 계정에 복사됨

**방법 B: 새 리포지토리 생성**
```bash
gh repo create my-claude-usage-sync --public
cd ~/my-claude-usage-sync
# 이 리포의 파일들 복사
```

### 2️⃣ index.html 수정 (중요!)

`index.html` 파일을 열고 **9번째 줄** 근처의 설정을 수정:

```javascript
// 이 부분을 본인의 GitHub 계정/리포지토리로 변경
const GITHUB_REPO = 'bohee-connectome/claude-usage-sync';  // ❌ 원본
const GITHUB_REPO = 'your-username/your-repo-name';        // ✅ 본인 것으로 변경
```

**예시:**
```javascript
const GITHUB_REPO = 'john-doe/my-claude-tracker';
```

### 3️⃣ GitHub Pages 활성화

1. GitHub 리포지토리 → **Settings** 탭
2. 왼쪽 메뉴에서 **Pages** 클릭
3. **Source** 설정:
   - Branch: `main` 선택
   - Folder: `/ (root)` 선택
   - **Save** 클릭
4. 1-2분 후 웹사이트 주소 확인:
   - `https://your-username.github.io/your-repo-name`

### 4️⃣ 각 디바이스에 설치

위의 "맥북 설정" 또는 "Windows PC 설정" 가이드를 따르되, **본인의 리포지토리**를 클론:

```bash
# 본인 리포 클론
gh repo clone your-username/your-repo-name claude-usage-tracker

# 나머지는 동일하게 설정
```

### 5️⃣ 완료!

- 터미널: `ccusage`, `ccusage-sync`, `ccusage-total` 사용
- 웹사이트: `https://your-username.github.io/your-repo-name` 접속

---

## 🔧 트러블슈팅

**"No usage data found":**
- 맥북: `~/.claude/projects/` 확인
- Windows: `%APPDATA%\Claude\projects\` 확인

**Git push 실패:**
```bash
gh auth status
gh auth login
```

**Python 없음:**
```bash
# Windows
winget install Python.Python.3.12

# macOS (Homebrew)
brew install python3
```

---

**Made with Claude Code** 🤖
