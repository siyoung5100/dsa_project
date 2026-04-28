"""BSP (Binary Space Partitioning) 기반 던전 생성.

명세서 §4.1 참고.
시간복잡도: O(R log R) 평균 (R = 방 수, max_depth로 상한 설정)
공간복잡도: O(W·H)

핵심 함수:
- generate_dungeon(W, H, min_leaf, max_depth, seed) -> Dungeon
- _split, _create_rooms, _connect (내부)
"""
