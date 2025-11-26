# 누적 토큰 추적 시스템 (Cumulative Token Tracking)

## 문제점
기존 시스템은 `.jsonl` 파일을 읽어서 토큰 수를 계산했습니다. Claude Code가 오래된 세션 파일을 자동으로 삭제하면 **토큰 사용 기록이 영구적으로 소실**되었습니다.

## 해결책
**누적 추적 시스템**: 한 번 카운트된 세션은 영구 데이터베이스에 저장되어, 파일이 삭제되어도 토큰 수는 계속 누적됩니다.

---

## 시스템 구성

### 1. 누적 데이터베이스
**위치**: `C:\Users\user\.claude\cumulative_usage.json`

**특징**:
- 처리한 모든 세션을 고유 ID로 추적
- 파일이 삭제되어도 카운트 유지
- 영구 보존 (백업 필수!)

### 2. 스크립트

#### `ccusage_cumulative.py` - 누적 추적기
```bash
ccusage
```
- 새로운 세션만 스캔하여 누적 카운트에 추가
- 이미 카운트된 세션은 건너뜀
- **파일이 삭제되어도 카운트 감소 없음**

#### `auto_sync.py` - 자동 동기화
```bash
ccusage-auto-sync
```
- 누적 추적 실행
- Git에 백업
- 멀티 디바이스 JSON 업데이트

#### `calculate_usage.py` - 레거시 (파일 기반)
```bash
ccusage-legacy
```
- 현재 존재하는 파일만 계산
- 파일 삭제 시 카운트 감소
- **사용 권장하지 않음**

---

## 사용 방법

### 1. 현재 누적 사용량 확인
```powershell
ccusage
```

**출력 예시**:
```
📈 CUMULATIVE CLAUDE USAGE (PERMANENT RECORD)
Period: October 1, 2025 - November 26, 2025

🆕 NEW SESSIONS THIS RUN:  0
✅ No new sessions found (all sessions already counted)

📊 CUMULATIVE TOTAL SESSIONS: 4,984

🔢 CUMULATIVE TOKEN TOTALS:
  Input Tokens:        123,293
  Output Tokens:       2,793,578
  Cache Creation:      41,365,003
  Cache Read:          346,231,237

💵 CUMULATIVE ESTIMATED COST (Sonnet 4.5):
  Input:        $0.37
  Output:       $41.90
  Cache Write:  $155.12
  Cache Read:   $103.87

  TOTAL:        $301.26

⚠️  This count is CUMULATIVE and PERMANENT
   Even if .jsonl files are deleted, counts remain!
```

### 2. 수동으로 Git에 백업
```powershell
ccusage-auto-sync
```

### 3. 자동 백업 설정 (권장!)
```powershell
# PowerShell을 관리자 권한으로 실행
cd C:\Users\user\claude-usage-tracker
.\setup_auto_sync.ps1
```

설정 완료 후:
- **매일 밤 11:59 PM**에 자동으로 실행
- 새 세션 카운트
- Git에 자동 백업

### 4. 작업 스케줄러 확인
```powershell
# 상태 확인
Get-ScheduledTask -TaskName "ClaudeUsageAutoSync"

# 즉시 실행 (테스트용)
Start-ScheduledTask -TaskName "ClaudeUsageAutoSync"

# 비활성화
Disable-ScheduledTask -TaskName "ClaudeUsageAutoSync"

# 활성화
Enable-ScheduledTask -TaskName "ClaudeUsageAutoSync"
```

---

## 데이터 복구 및 백업

### 누적 데이터베이스 백업
```powershell
# 수동 백업
Copy-Item "$env:USERPROFILE\.claude\cumulative_usage.json" `
          "$env:USERPROFILE\claude-usage-tracker\backups\cumulative_$(Get-Date -Format 'yyyyMMdd').json"
```

### Git 히스토리에서 복구
```bash
cd ~/claude-usage-tracker
git log --all -- data/yangpyungpc.json
git checkout <commit-hash> -- data/yangpyungpc.json
```

---

## 멀티 디바이스 사용

각 디바이스에서:

1. **auto_sync.py 수정**:
   ```python
   DEVICE_ID = "yangpyungpc"  # 디바이스별로 고유 이름 설정
   ```

2. **자동 동기화 설정**:
   ```powershell
   .\setup_auto_sync.ps1
   ```

3. **전체 사용량 확인**:
   ```powershell
   ccusage-total  # 모든 디바이스 합산
   ```

---

## 12월 31일까지 1억 토큰 목표 추적

### 현재 진행 상황 확인
```powershell
ccusage
```

### 목표까지 남은 토큰
```python
# Python으로 계산
import json
from pathlib import Path

db_file = Path.home() / ".claude" / "cumulative_usage.json"
db = json.load(open(db_file))
cumulative = db["cumulative_usage"]

total_processed = (
    cumulative["input_tokens"] +
    cumulative["output_tokens"] +
    cumulative["cache_creation_tokens"]
)

target = 100_000_000
remaining = target - total_processed

print(f"현재: {total_processed:,} tokens")
print(f"목표: {target:,} tokens")
print(f"남은 토큰: {remaining:,}")
print(f"진행률: {(total_processed/target)*100:.2f}%")
```

---

## 중요 사항

### ✅ 해야 할 것
1. **정기적으로 `ccusage-auto-sync` 실행** (자동화 권장)
2. **누적 데이터베이스 백업** (`cumulative_usage.json`)
3. **Git 리포지토리 정기 확인**

### ❌ 하지 말아야 할 것
1. **`cumulative_usage.json` 파일 삭제하지 않기**
2. **직접 수동 편집하지 않기**
3. **레거시 스크립트(`ccusage-legacy`)로 공식 기록하지 않기**

---

## 문제 해결

### Q: 세션 수가 감소했어요
A: `ccusage` (누적 버전) 사용 중이면 **절대 감소하지 않습니다**.
   `ccusage-legacy`를 사용했다면 누적 버전으로 전환하세요.

### Q: Git push 실패
A: 로컬 데이터는 안전합니다. 나중에 수동으로 push하면 됩니다:
```bash
cd ~/claude-usage-tracker
git pull --rebase
git push
```

### Q: 데이터베이스 초기화하고 싶어요
A: **절대 권장하지 않습니다!** 백업 후에만:
```powershell
# 백업
Copy-Item "$env:USERPROFILE\.claude\cumulative_usage.json" `
          "$env:USERPROFILE\claude-usage-tracker\backups\cumulative_backup.json"

# 삭제 (신중히!)
Remove-Item "$env:USERPROFILE\.claude\cumulative_usage.json"

# 다음 ccusage 실행 시 새로 생성됨
```

---

## 시스템 동작 원리

### 세션 고유 ID 생성
각 세션은 다음 정보로 고유 ID 생성:
- 파일명
- 타임스탬프
- 토큰 수 (일부)

```python
session_id = md5(f"{filename}_{timestamp}_{input_tokens}_{output_tokens}")
```

### 증분 카운팅
1. 모든 `.jsonl` 파일 스캔
2. 각 세션의 고유 ID 계산
3. 데이터베이스에 이미 있는지 확인
4. 새 세션만 카운트에 추가
5. 데이터베이스 업데이트

### 영구 보존
- 한 번 처리된 세션은 `processed_sessions`에 영구 저장
- 파일이 삭제되어도 `processed_sessions`에 남음
- 누적 카운트는 절대 감소하지 않음

---

**Created & Directed by Bohee Lee**
**Built with Claude Code**

**목표: 12월 31일까지 1억 토큰 입증!** 🎯
