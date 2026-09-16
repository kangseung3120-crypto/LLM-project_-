뉴스 요약 QA 시스템 — 로컬 LLM 모델 선정 프로젝트

사용자가 질문과 관련 기사 원문을 직접 입력하면 로컬 LLM이 핵심 사실을 요약하고 기사 간 논조 차이를 비교해서 답변하는 QA 시스템을 만들기 위해, 후보 모델을 선정하는 과정을 정리한 문서입니다.

1. 사용 사례

사용자가 궁금한 주제/질문과 관련 기사(1~2개)를 직접 입력하면, 로컬 LLM이
핵심 사실 요약, 2) 기사 간 논조/관점 차이를 답변하는 QA 시스템
Task를 Chat이 아닌 QA로 설계 (근거 문서 기반 답변이 정확성 요구사항에 더 부합)
기사는 항상 사용자가 직접 붙여넣음 (검색 자동화는 비용·네이버 API 약관 문제로 제외)

2. 요구사항
항목	확정 내용
Language	한국어
Model Size	8GB VRAM에서 오프로드 없이 구동 (다운로드 용량 5~6GB 이하)
License	부트캠프 비상업 프로젝트 → 상업/비상업 라이선스 모두 허용 가능
Context Length	입력 기사 1~2개(약 2~4K 토큰), 출력 길이 제한 없음
GPU	실측 VRAM 8151MiB, 드라이버 592.01
Task	QA (질문 + 기사 직접 입력)

3. 후보 모델
항목	Qwen2.5-7B-Instruct	EXAONE 3.5-7.8B-Instruct
개발사	Alibaba	LG AI Research
Ollama 태그	qwen2.5:7b	exaone3.5:7.8b
용량	4.7GB	4.8GB
라이선스	Apache 2.0	연구/비상업 목적 허용
체급이 거의 같은 두 모델(7.62B vs 7.8B)을 선정해 공정한 비교가 되도록 했습니다.

Qwen2.5:7B (https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)

EXAONE3.5:7.8B (https://huggingface.co/LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct-AWQ)

4. 평가 설계 (STEP 5·6)
고정 질문 10개, 정상 사례 6 / 경계 사례 2 / 정보부족·범위밖 사례 2로 구성
채점 기준 5개: 정확성 / 핵심정보누락 / 지시·형식준수 / 한국어표현 / 정보부족시대응
모델 2개 x 질문 10개 x 반복 2회 = 모델당 20회 본실험 + 워밍업 1회(집계 제외)
동일 설정(temperature=0, num_ctx=4096) 적용

5. 로컬 실험 결과
지표	qwen2.5:7b	exaone3.5:7.8b
호출 성공률	20/20	20/20
정확성 (전체 10문항)	4.20	4.25
핵심정보누락	3.90	4.10
지시형식준수	4.20	4.30
한국어표현	5.00	4.90
평균 응답시간	4.12초	5.02초
VRAM 사용량	4528 MiB	4945 MiB

EXAONE: 정확성, 핵심정보, 지시 형식에서 근소하게 우세
Qwen: 한국어 표현에서 근소하게 우세
두 모델 모두 40/40 호출 성공
같은 질문을 2회 반복하여 응답의 일관성을 확인했습니다.

Qwen: 10개 질문 모두 결론 일치
EXAONE: Q3, Q5, Q9에서 결론이 변경됨
→ 재현성 측면에서는 Qwen이 더 안정적인 결과를 보였습니다

6. Cloud 비교
미리 선정한 5개 질문(Q1,Q3,Q5,Q7,Q9)을 GPT-5.6 Luna에 1회씩 실행 (로컬은 2회 — 반복 수 차이 있음에 유의).

지표	qwen2.5:7b (n=10)	exaone3.5:7.8b (n=10)	gpt-5.6-luna (n=5)
정확성	4.6	4.3	5.0
핵심정보누락	3.8	4.0	4.6
지시형식준수	4.0	4.0	4.8
한국어표현	5.0	4.8	5.0
응답시간	4.21초	5.36초	4.83초(네트워크 포함)
비용	$0(전력비 제외)	$0(전력비 제외)	$0.0036(5건 합계)

Luna가 품질에서 확실히 앞섰고, 비용도 사실상 무의미한 수준이었습니다.

7. 최종 선정

선정 모델: qwen2.5:7b

품질은 Luna가 앞섰지만, 이 프로젝트의 목적(기사 원문이 외부로 나가지 않는 로컬 시스템, 오프라인 독립 동작)을 우선해 로컬 모델 중 선정했습니다. Qwen과 EXAONE 사이에서는:

재현성: Qwen 100% vs EXAONE 70% — 판단 근거로 재사용할 시스템에서 중요한 차이
라이선스: Qwen은 Apache 2.0으로 상업적 활용까지 열려 있음
품질 차이는 근소하고 기준별로 엇갈려, 위 두 요인이 결정적이었습니다

Cloud(Luna)는 품질이 최우선이고 외부 전송이 허용되는 상황의 대안으로 별도 권고합니다.

8. 한계점
평가셋이 10문항(Cloud 비교는 5문항)으로 소규모라 통계적 유의성 확보는 어려움
8GB VRAM 1대에서만 측정, 다른 하드웨어에서는 결과가 달라질 수 있음
Q7·Q8은 원래 설계한 실제 기사를 찾지 못해 합성(가상) 기사로 대체
Cloud는 1회, 로컬은 2회 실행해 재현성 비교의 엄밀도가 다름

9. 파일 구성
파일	역할
채점결과_완료.md	40건 전체 채점 결과 및 근거
채점기준표.md	5개 채점 기준 및 점수 근거
최종_모델선정보고서.md	 최종 선정 보고서
Local_vs_Cloud_비교.md  6개 항목 비교표
README.md

01_ollama_old_chat.py 로컬 모델 호출
02_ollama_chat_local.py	로컬 모델 실험 스크립트 (워밍업+2회 반복)
03_summarize_local.py  local 결과 집계 스크립트
04_luna_chat_cloud.py	Cloud(Luna) 비교 실험 스크립트
05_summarize_cloud.py	Cloud 결과 집계 스크립트
cloud_summary.json	Cloud 집계 결과
eval_questions.py	평가 질문 10개 (기사 원문 포함)
summary.json   local 집계 결과



10. 실행 방법
powershell
# 로컬 실험
ollama pull qwen2.5:7b
ollama pull exaone3.5:7.8b
ollama serve
python run_experiment.py
python export_report.py
python summarize.py

# Cloud 실험
pip install openai --break-system-packages
python run_cloud_experiment.py   # 실행 중 API 키 입력 프롬프트가 뜸
python summarize_cloud.py