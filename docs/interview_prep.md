# 🏆 DS&A 프로젝트 발표 조교 Q&A 인터뷰 대비서 (interview_prep.md)

이 문서는 기말 프로젝트 평가 가이드라인에 명시된 질문 유형에 맞추어, **5단계 표준 답변 템플릿(State - Justify - Point - Compare - Complexity)** 구조를 백퍼센트 반영해 작성한 인터뷰 모범 답안 가이드라인입니다. 발표 직전 이 스크립트를 숙지하시면 만점 획득이 보장됩니다.

---

## 💡 Q&A 모범 답변 5단계 템플릿 가이드
평가관의 질문이 떨어지면 당황하지 않고 아래 5단계를 순서대로 구술합니다:
1. **[State]** 적용한 자료구조 또는 알고리즘을 단 한 문장으로 선언합니다.
2. **[Justify]** 왜 이 자료구조/알고리즘이 기능적 요건에 최적으로 부합하는지 설명합니다.
3. **[Point]** 우리 프로젝트 소스코드 내의 정확한 파일 및 함수/클래스명을 짚어줍니다.
4. **[Compare]** 대체 가능한 자료구조/알고리즘 하나를 언급하고 그 한계점(단점)을 비교합니다.
5. **[Complexity]** 최악/평균 시간복잡도 및 공간복잡도를 명확한 수식과 함께 대답합니다.

---

## 📂 6대 핵심 기능별 Q&A 모범 답안

### 🗺️ 1. Dungeon Map (BSP Tree 절차적 공간 분할)

* **Q: 던전 맵을 생성하고 표현하기 위해 어떤 자료구조와 알고리즘을 사용했나요?**
  * **[State]** 저희는 공간을 이진 트리로 표현하는 **BSP(Binary Space Partitioning) 알고리즘**을 사용하여 던전 맵을 표현했습니다.
  * **[Justify]** 던전 생성 시 방들이 서로 불규칙하게 겹치지 않고 정형화된 직사각형 방들과 이를 잇는 복도를 체계적으로 배치하기 위해 공간 분할 트리 구조가 가장 적합하다고 판단했습니다.
  * **[Point]** 구현부는 [map/bsp.py](file:///c:/Claude/DSA_moved/dungeon_crawler/map/bsp.py#L51) 파일의 `generate_dungeon` 함수와 `BSPNode` 클래스에 작성되어 있습니다.
  * **[Compare]** 대체 알고리즘인 **BFS/DFS 기반 랜덤 플러드필 방식**은 맵을 불규칙하고 꼬불꼬불한 동굴처럼 뚫어 가독성이 저하되지만, BSP는 분할 비율 조정을 통해 깔끔한 방 구조를 보장합니다. 또한 리프 노드 테두리에 **최소 2칸의 패딩(Padding=2)**을 주어 방들이 무분별하게 맞붙는 시각적 결함을 사전에 완전 차단했습니다.
  * **[Complexity]** 공간 분할 깊이를 $D$라 할 때 시간복잡도는 평균 $O(2^D \log(2^D))$ 이며, 맵 전체 타일을 보관하는 공간복잡도는 $O(W \times H)$ 입니다.

---

### ⏪ 2. Undo System (Double-Ended Queue / Deque)

* **Q: 되돌리기(Undo) 기능을 구현하기 위해 왜 스택(LIFO) 형태의 자료구조를 선택했나요?**
  * **[State]** 저희는 파이썬 표준 라이브러리의 **덱(collections.deque)**을 활용해 LIFO 구조를 지닌 **Command 패턴 스택**을 구현했습니다.
  * **[Justify]** 되돌리기 기능은 항상 "가장 최근에 취한 행동"을 첫 번째 순위로 취소해야 하는 **LIFO(Last-In, First-Out)** 구조에 대응되므로 덱 스택 구조가 최적입니다.
  * **[Point]** 소스코드는 [systems/undo.py](file:///c:/Claude/DSA_moved/dungeon_crawler/systems/undo.py#L22)의 `UndoSystem` 및 [core/types.py](file:///c:/Claude/DSA_moved/dungeon_crawler/core/types.py#L183)의 `MoveAction`, `AttackAction` 등 Action 파생 클래스들에 녹아 있습니다.
  * **[Compare]** 대체 구조인 **큐(Queue)**는 FIFO(First-In, First-Out) 구조이기 때문에, 되돌리기를 실행하면 게임 시작 후 최초로 취했던 첫 번째 행동이 복원되어 시간적 역순 롤백이 불가능합니다.
  * **[Complexity]** 액션의 스택 푸시(Push) 및 팝(Pop)은 항상 양방향 포인터를 이용한 **$O(1)$ 상수 시간** 내에 완료됩니다. 되돌리기 최대 보존 한도(Limit)를 30개로 제약하여 공간복잡도는 $O(N)$의 한계를 지켜 메모리 누수가 없습니다.

---

### ⏳ 3. Turn Management (heapq / Min-Heap)

* **Q: 모든 캐릭터의 턴 순서를 어떻게 공정하게 배분했으며, 왜 단순 큐(Queue) 대신 힙(Heap)을 썼나요?**
  * **[State]** 플레이어와 몬스터의 개별 턴 배정을 위해 최소값 추출이 용이한 **우선순위 큐(Min-Heap / heapq)**를 활용했습니다.
  * **[Justify]** 행동 비용(cost)과 속도(speed) 가중치를 결합한 공식($next\_tick = current\_tick + cost \times 100 // speed$)에 따라 턴 개시 시점을 산출하고, 이를 시각 축 정렬로 정교하게 관리하기 위함입니다.
  * **[Point]** 구현부는 [systems/turn_manager.py](file:///c:/Claude/DSA_moved/dungeon_crawler/systems/turn_manager.py#L22) 파일의 `TurnManager` 클래스에 명세되어 있습니다.
  * **[Compare]** 대체 구조인 **일반 큐(Queue)**는 모든 캐릭터의 속도가 같을 때는 기능하지만, 속도 편차가 존재하여 턴을 가로채거나 가속화하는 우선순위 개념을 연산할 수 없습니다. 
  * **[Complexity]** 턴 예약(`schedule`)과 팝(`next_actor`)은 **$O(\log K)$** 시간복잡도를 지닙니다. 특히 사망한 몬스터를 힙의 중간에서 제거하는 선형 시간 $O(K)$의 비효율성을 방지하기 위해 지연 삭제 셋(`_dead: set`)을 활용한 **Lazy Deletion** 방식을 도입하여 $O(\log K)$ 상환 성능을 유지했습니다.

---

### 🎒 4. Item Inventory (Double Hash Table)

* **Q: 인벤토리를 List 대신 Hash Table(dict)로 구현한 이유는 무엇인가요?**
  * **[State]** 저희는 아이템 카테고리를 대분류 키로 두고 아이템 고유 ID를 소분류 키로 맵핑하는 **이중 해시 테이블(Nested Dict)**을 활용해 인벤토리를 구축했습니다.
  * **[Justify]** 아이템 습득 시 수량 증가 및 사용 시 감소 연산을 수행하기 위해 순회 없이 즉시 타깃 슬롯을 점검하고 변경하기 위함입니다.
  * **[Point]** 소스코드는 [systems/inventory.py](file:///c:/Claude/DSA_moved/dungeon_crawler/systems/inventory.py#L47) 파일의 `Inventory` 클래스에 기술되어 있습니다.
  * **[Compare]** 대체재인 **연결 리스트(List)**나 배열은 중복 아이템의 탐색 및 수량 갱신을 위해 선형 순회 $O(N)$이 발생하며, 아이템 종류가 늘어날수록 조회가 느려집니다.
  * **[Complexity]** 해시 탐색 평균 시간복잡도는 **$O(1)$** 상수 시간이며, 최악의 해시 충돌 시에도 $O(K)$ ($K$ = 해당 카테고리 내 아이템 종류 수)의 극도로 미미한 비용만 소요됩니다. 공간 복잡도는 $O(M)$ ($M$ = 전체 등록된 아이템 수)입니다.

---

### 🧠 5. Enemy AI (A* Pathfinding & 캐시 슬라이싱)

* **Q: 적 몬스터의 추적 알고리즘으로 A*를 선택한 이유와 대체재와의 차이는 무엇인가요?**
  * **[State]** 최적의 목적지 안내를 위해 맨해튼 거리 휴리스틱을 결합한 **A* 경로 탐색 알고리즘**을 도입했습니다.
  * **[Justify]** 벽(장애물)이 존재하는 격자 맵 환경에서 맹목적인 탐색을 건너뛰고 최단 실경로를 실시간으로 가장 빠르게 검출하기 위해서입니다.
  * **[Point]** 구현 코드는 [systems/ai.py](file:///c:/Claude/DSA_moved/dungeon_crawler/systems/ai.py#L77)의 `EnemyAI`와 `a_star` 함수에 명세되어 있습니다.
  * **[Compare]** 대체재인 **BFS(너비 우선 탐색)**는 최단 거리를 보장하지만 가중치가 없는 맵 전체를 동심원 형태로 맹목 전수 탐색하여 연산량이 $O(V+E)$로 비대해집니다. 반면 A*는 방향성을 지닌 휴리스틱을 결합하여 탐색 노드 수를 획기적으로 줄입니다.
  * **[Complexity]** 시간복잡도는 평균 $O(V \log V)$이며 ($V$ = 탐색 영역 타일 수), 공간복잡도는 $O(V)$ 입니다. 특히 몬스터가 매 턴 A*를 재계산하는 병목을 막고자 **경로 캐싱 및 동적 캐시 슬라이싱(Slicing) 기술**을 얹어 연산 부하를 $O(1)$로 감축시켰습니다.

---

### 🏆 6. Leaderboard (자체 구현 AVL Tree & Size 필드)

* **Q: 리더보드를 단순히 정렬된 파일로 쓰지 않고 균형 이진 트리(AVL)로 직접 구현한 이유는 무엇인가요?**
  * **[State]** 자가 균형 이진 탐색 트리인 **AVL Tree**를 파이썬으로 자체 클래스 설계하여 리더보드를 구축했습니다.
  * **[Justify]** 새로운 점수가 지속적으로 등록되더라도 트리의 높이 균형(Balance Factor)을 스스로 회복하여 탐색 성능을 항상 보장하기 위함입니다.
  * **[Point]** 소스코드는 [persistence/avl_tree.py](file:///c:/Claude/DSA_moved/dungeon_crawler/persistence/avl_tree.py#L32) 의 `AVLTree` 및 `Node` 클래스에 엄격하게 쓰여 있습니다.
  * **[Compare]** 대체 방식인 **전체 리스트 정렬(Full Sorting)** 방식은 새로운 데이터가 추가될 때마다 $O(N \log N)$의 고비용 정렬을 실행해야 하므로 데이터가 수만 건으로 누적될 때 성능 병목이 발생합니다.
  * **[Complexity]** 점수 추가(`insert`)와 검색(`search`) 시간복잡도는 균형 유지 회전(Rotation) 연산에 의해 **최악의 상황에서도 항상 $O(\log N)$**에 보장됩니다. 
  * **[💡 가산점 포인트]** 노드 구조체 내부에 하위 서브트리 전체 노드 수를 유지하는 **`size` 필드**를 추가로 구현하여, **전체 정렬 없이 임의의 K번째 랭킹 조회(`kth`) 및 특정 스코어의 랭킹 계산(`rank`)을 오직 $O(\log N)$에 다이렉트 수행**해내는 극대화된 알고리즘 설계 능력을 갖추었습니다.
