# 1️⃣ 프로젝트 개요

<aside>
🎯

개인 또는 팀으로 서비스 상황을 정하고, **로컬 LLM 2개를 Ollama로 실행·비교한 뒤 적합한 모델 1개를 선정**합니다. 진행 기간은 **5일**이며, Cloud API 모델 1개에는 공통 질문 일부를 적용해 실제 운영 방식도 검토합니다.

### 필수·선택 범위

| 구분 | 수행 범위 |
| --- | --- |
| 필수 | 사용 사례와 요구사항 정의, Hugging Face 모델 정보 조사, 서로 다른 로컬 모델 2개 실행, 동일 질문 기반 품질·성능 비교, 소규모 Local–Cloud 비교, 모델 선정과 발표 |
| 선택 | 세 번째 로컬 모델 비교, Transformers 직접 실행, 동일 모델의 양자화 버전 비교, Sentence Transformers 임베딩 실습 |
| 공통 환경 | Windows 수업용 노트북, Ollama, VS Code + uv + Python 3.12. 2번 선행 가이드의 실행 환경을 이어서 사용 |
| 산출물 | GitHub 저장소 하나에 실행 코드, 환경 정보, 실험 기록, 비교표, 최종 선정 근거를 함께 제출 |

- 이번 프로젝트에서 배우는 내용
    
    ### 1. 오픈소스 LLM 직접 실행
    
    - Hugging Face Model Card, 모델 특성, License 조사
    - Ollama로 로컬 모델 다운로드·실행
    - Python 호출 예제를 바탕으로 반복 실행, 추가 측정, 결과 기록 구성
    - Transformers / PyTorch 직접 모델 로딩은 선택 실습
    
    ### 2. 모델 정보 읽기
    
    - Model Card, Parameter Size, License, Context Length, Tokenizer, Chat Template, Quantization, 공개 Benchmark, VRAM 요구량
    
    ### 3. 모델 성능과 특성 비교
    
    - Quality: 답변 정확성, Instruction Following, 한국어 품질
    - Performance: 응답 시간, Token 생성 속도, VRAM 사용량
    - Model Characteristics: Model Size, Context Length, Quantization, License
    
    ### 4. Local LLM과 Cloud LLM 비교
    
    - 품질, 비용, 데이터 통제, 인프라, 커스터마이징, 운영 부담을 비교하고 서비스 상황에 맞는 운영 방식을 제안합니다.
- 기존 강의에서 배운 내용 활용
    
    
    | 기존 학습 내용 | 프로젝트 활용 |
    | --- | --- |
    | Git & GitHub | 프로젝트 Repository 관리 및 협업 |
    | AI Literacy | Closed API와 Open-source LLM 비교 |
    | 기초 수학 / 선형대수 | 벡터·유사도 이해, 선택 임베딩 실습 결과 해석 |
    | 딥러닝 기초 | Tensor, GPU, 모델 실행 구조 이해 |
    | Transformer / Tokenizer | LLM 구조와 모델별 Tokenization 방식 이해 |
    | Hugging Face / Model Card / License | 모델 저장소·설정·특성·사용 가능 여부 판단 |
    | Chat Template / Generation Decoding | Chat 모델 입력 형식과 모델별 출력 특성 비교 |
    | Prompt Engineering | 모델 비교를 위한 동일 Prompt 설계 |
    | Structured Output | 필요한 태스크의 출력 형식 검사. JSON 강제, Tool Calling, 멀티모달 구현은 요구하지 않음 |
    
    구현이 막히면 Python의 파일/pathlib/JSON/JSONL, Hugging Face Hub와 입력 디버깅, Baseline·Few-shot·평가 루브릭, Timeout·Retry·Fallback·Latency logging, GitHub 저장소 구성과 Issue 관리 내용을 복습합니다.
    
- 프로젝트 종료 시 갖게 되는 역량
    - Hugging Face에서 필요한 모델을 탐색하고 Model Card와 License를 읽을 수 있습니다.
    - Ollama와 Python으로 로컬 모델 2개를 호출하고 결과를 기록할 수 있습니다.
    - 모델별 품질, 속도, 메모리 사용량 차이를 측정하고 Quantization의 영향을 이해할 수 있습니다.
    - Local–Cloud의 실측 결과와 운영 조건을 구분해 모델과 실행 위치를 설명할 수 있습니다.
    - 선택 실습을 수행한 경우 Sentence Transformers로 Embedding을 만들고 유사도를 해석할 수 있습니다.
