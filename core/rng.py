"""seed 고정용 랜덤 래퍼.

테스트 가능성을 위해 모든 무작위성은 이 모듈을 통해 주입한다.
전역 random 호출은 금지.
"""

import random


class RNG:
    """랜덤 상태를 관리하는 객체.

    seed를 고정하여 테스트 재현성을 확보할 수 있다.
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    def randint(self, a: int, b: int) -> int:
        """[a, b] 범위의 정수 반환."""
        return self._rng.randint(a, b)

    def random(self) -> float:
        """[0.0, 1.0) 범위의 실수 반환."""
        return self._rng.random()

    def choice(self, seq: list | tuple) -> any:
        """시퀀스에서 무작위 원소 하나 선택."""
        return self._rng.choice(seq)

    def shuffle(self, x: list) -> None:
        """리스트를 제자리에서 섞음."""
        self._rng.shuffle(x)
