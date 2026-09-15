import json
import time
from datetime import datetime, timezone

from ollama import Client

# ── 동일 조건 실험 설정 (두 모델 모두 이 값 그대로 적용) ────────────
MODELS = ["qwen2.5:7b", "exaone3.5:7.8b"]
GENERATION_SETTINGS = {"temperature": 0, "num_ctx": 4096}
# num_predict를 넣지 않음 -> 출력 길이 제한 없음 (두 모델 동일)
# 대화 이력(messages)은 매 호출마다 system+user 2개만 보냄 -> 이전 대화 기억 없음 (두 모델 동일)
# 차이가 있다면: 모델별 내장 채팅 템플릿(포맷)은 Ollama가 모델마다 다르게 자동 적용함
# -> 이는 통제 불가능한 모델 자체의 차이로, 결과 해석 시 감안해야 함
REPEATS_PER_QUESTION = 2
WARMUP_QUESTION = "안녕하세요, 간단히 인사해주세요."  # 평가 질문과 무관한 워밍업 전용 질문

# 이번 실행이 "본 실험"인지 "재시도"인지 "추가 실험"인지 표시.
# 실패한 항목만 다시 돌릴 때는 이 값을 "retry"로 바꿔서 실행 (본 실험 집계와 안 섞이게)
RUN_TYPE = "main"  # "main" | "retry" | "extra"

SYSTEM_PROMPT = (
    "당신은 뉴스 분석을 도와주는 어시스턴트입니다. "
    "사용자가 질문과 함께 기사 원문을 제공하면, 오직 그 기사 내용에 근거해서만 답변하세요. "
    "답변은 다음 두 부분으로 구성합니다.\n"
    "1) 핵심 사실 요약: 기사에서 확인되는 핵심 내용을 간결하게 정리\n"
    "2) 기사 간 논조/관점 차이: 두 기사의 관점이나 강조점에 차이가 있으면 설명하고, "
    "차이가 없다면 '논조 차이 없음'이라고 명시. 기사가 1개뿐이면 이 항목은 생략.\n"
    "기사에 없는 내용은 절대 추측해서 만들어내지 마세요."
)
# ────────────────────────────────────────────────────────────────

client = Client(host="http://127.0.0.1:11434", timeout=180)


def get_running_model_info(model_name):
    """client.ps()로 현재 메모리에 올라온 모델의 digest/양자화/VRAM 사용량을 찾는다.
    실패하거나 못 찾으면 (None, 사유) 를 돌려준다."""
    try:
        running = client.ps()
    except Exception as e:
        return None, f"ps() 호출 실패: {e}"

    for m in running.models:
        if m.model == model_name:
            info = {
                "digest": m.digest,
                "quantization_level": m.details.quantization_level,
                "size_bytes": m.size,
                "size_vram_bytes": m.size_vram,
            }
            return info, None

    return None, "ps() 결과에서 해당 모델을 찾지 못함 (이미 언로드되었을 수 있음)"


def get_context_length(model_name):
    """client.show()에서 실제 적용된 context_length를 찾는다.
    모델 아키텍처마다 키 이름이 달라서(예: qwen2.context_length) 이름에
    'context_length'가 들어간 키를 찾는 방식으로 처리."""
    try:
        info = client.show(model_name)
    except Exception as e:
        return None, f"show() 호출 실패: {e}"

    model_info = info.modelinfo if hasattr(info, "modelinfo") else None
    if not model_info:
        return None, "show() 결과에 modelinfo 없음"

    for key in model_info:
        if "context_length" in key:
            return model_info[key], None

    return None, "context_length 관련 키를 찾지 못함"


def classify_load_status(size_bytes, size_vram_bytes):
    """size와 size_vram을 비교해 GPU/CPU 적재 상태를 문자열로 반환."""
    if size_bytes is None or size_vram_bytes is None:
        return "확인 불가"
    if size_vram_bytes <= 0:
        return "CPU만 적재"
    if size_vram_bytes >= size_bytes:
        return "GPU 전체 적재"
    return "GPU+CPU 혼합 적재"


def call_model(model, user_prompt):
    """모델 1회 호출. 성공하면 (record_dict, True), 실패하면 (record_dict, False)를 반환.
    실패해도 예외를 밖으로 던지지 않고, 실패 사실 자체를 기록으로 남긴다."""
    t0 = time.time()
    try:
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            options=GENERATION_SETTINGS,
        )
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "status": "error",
            "error_message": str(e),
            "raw_answer": None,
            "wall_clock_seconds": round(elapsed, 2),
            "load_duration_seconds": None,
            "eval_count_tokens": None,
            "tokens_per_second": None,
            "tokens_per_second_note": "호출 실패로 측정 불가",
        }, False

    elapsed = time.time() - t0

    eval_count = response.eval_count
    eval_duration = response.eval_duration  # 나노초
    load_duration = response.load_duration  # 나노초

    if eval_count and eval_duration and eval_duration > 0:
        tok_per_sec = eval_count / (eval_duration / 1_000_000_000)
        tok_per_sec_note = None
    else:
        tok_per_sec = None
        tok_per_sec_note = "eval_count 또는 eval_duration 값이 없거나 0 이하라 계산 불가"

    load_duration_seconds = load_duration / 1_000_000_000 if load_duration is not None else None

    # 실행 시점의 VRAM/digest/양자화/context_length 조회
    running_info, running_note = get_running_model_info(model)
    context_length, ctx_note = get_context_length(model)

    if running_info:
        vram_mib = running_info["size_vram_bytes"] / 1024 / 1024
        digest = running_info["digest"]
        quantization_level = running_info["quantization_level"]
        load_status = classify_load_status(
            running_info["size_bytes"], running_info["size_vram_bytes"]
        )
    else:
        vram_mib = None
        digest = None
        quantization_level = None
        load_status = "확인 불가"

    return {
        "status": "success",
        "error_message": None,
        "raw_answer": response.message.content,
        "wall_clock_seconds": round(elapsed, 2),
        "load_duration_seconds": (
            round(load_duration_seconds, 3) if load_duration_seconds is not None else None
        ),
        "eval_count_tokens": eval_count,
        "tokens_per_second": round(tok_per_sec, 1) if tok_per_sec else None,
        "tokens_per_second_note": tok_per_sec_note,
        "vram_used_mib": round(vram_mib, 1) if vram_mib is not None else None,
        "vram_note": running_note,
        "model_digest": digest,
        "quantization_level": quantization_level,
        "context_length": context_length,
        "context_length_note": ctx_note,
        "cpu_gpu_load_status": load_status,
    }, True


def build_user_prompt(question):
    if question["article_2"] is None:
        return "질문: " + question["question"] + "\n\n--- 기사 ---\n" + question["article_1"]
    return (
        "질문: " + question["question"]
        + "\n\n--- 기사 1 ---\n" + question["article_1"]
        + "\n\n--- 기사 2 ---\n" + question["article_2"]
    )


from eval_questions import EVAL_QUESTIONS
eval_questions = EVAL_QUESTIONS

out = open("results.jsonl", "a", encoding="utf-8")  # append: 재시도/추가실험이 기존 기록을 안 지움

total_runs = len(MODELS) * (1 + len(eval_questions) * REPEATS_PER_QUESTION)
run_no = 0
success_count = {}  # 모델별 성공 수
attempt_count = {}  # 모델별 시도 수 (워밍업 제외, RUN_TYPE=="main" 기준)

for model in MODELS:
    success_count[model] = 0
    attempt_count[model] = 0

    # ── 워밍업 1회: 본 집계와 분리해서 기록 (run_type="warmup") ──
    run_no = run_no + 1
    print(f"[{run_no}/{total_runs}] {model} 워밍업 중...")
    result, ok = call_model(model, WARMUP_QUESTION)

    warmup_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "run_type": "warmup",
        "repeat_no": None,
        "question_id": None,
        "settings": GENERATION_SETTINGS,
    }
    warmup_record.update(result)
    out.write(json.dumps(warmup_record, ensure_ascii=False) + "\n")

    # ── 본 실험: 질문 10개 x 반복 2회 ──────────────────────────
    for q in eval_questions:
        user_prompt = build_user_prompt(q)

        for repeat_no in range(1, REPEATS_PER_QUESTION + 1):
            run_no = run_no + 1
            print(f"[{run_no}/{total_runs}] {model} - {q['id']} ({repeat_no}회차) 호출 중...")

            result, ok = call_model(model, user_prompt)

            attempt_count[model] = attempt_count[model] + 1
            if ok:
                success_count[model] = success_count[model] + 1

            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": model,
                "run_type": RUN_TYPE,
                "repeat_no": repeat_no,
                "question_id": q["id"],
                "사례유형": q["사례유형"],
                "settings": GENERATION_SETTINGS,
                "question": q["question"],
                "article_1": q["article_1"],
                "article_2": q["article_2"],
                "기대결과": q["기대결과"],
            }
            record.update(result)
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

out.close()

print(f"\n완료. results.jsonl에 이번 실행분이 추가되었습니다 (run_type={RUN_TYPE}).")
print("\n[모델별 호출 성공 수 / 전체 시도 수] (워밍업 제외)")
for model in MODELS:
    print(f"  {model}: {success_count[model]} / {attempt_count[model]}")