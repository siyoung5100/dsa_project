"""map/bsp.py 단위 테스트.

명세서 §5.1 시나리오 참고:
- 결정론(seed 고정 → 동일 결과)
- 방 수 범위 검증
- 모든 방의 BFS 도달성
- 방끼리 겹치지 않음
"""

import pytest

pytestmark = pytest.mark.skip(reason="BSP 미구현 — 모듈 작성 후 활성화")
