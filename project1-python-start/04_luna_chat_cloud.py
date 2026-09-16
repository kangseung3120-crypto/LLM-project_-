import json
import time
from datetime import datetime, timezone
from getpass import getpass

from openai import APIError, APITimeoutError, OpenAI
from eval_questions import EVAL_QUESTIONS

MODEL = "gpt-5.6-luna"

# 2026년 9월 기준 공개 요금 (1M 토큰당) - 실제 청구와 다를 수 있음, 추정용
PRICE_PER_MTOK_INPUT = 0.20
PRICE_PER_MTOK_OUTPUT = 1.20

# 로컬은 출력 길이 제한이 없었지만(num_predict 미설정), Cloud는 비용 관리를 위해
# 넉넉한 한도를 둠 -> 이 차이는 결과 해석 시 반드시 명시할 것
MAX_OUTPUT_TOKENS = 1024

SYSTEM_PROMPT = (
    "당신은 뉴스 분석을 도와주는 어시스턴트입니다. "
    "사용자가 질문과 함께 기사 원문을 제공하면, 오직 그 기사 내용에 근거해서만 답변하세요. "
    "답변은 다음 두 부분으로 구성합니다.\n"
    "1) 핵심 사실 요약: 기사에서 확인되는 핵심 내용을 간결하게 정리\n"
    "2) 기사 간 논조/관점 차이: 두 기사의 관점이나 강조점에 차이가 있으면 설명하고, "
    "차이가 없다면 '논조 차이 없음'이라고 명시. 기사가 1개뿐이면 이 항목은 생략.\n"
    "기사에 없는 내용은 절대 추측해서 만들어내지 마세요."
)

# 키는 실행할 때 입력합니다. 화면에 표시되거나 파일에 저장되지 않습니다.
api_key = getpass("OpenAI API 키를 붙여넣고 Enter (화면에 보이지 않음): ").strip()
if not api_key:
    raise SystemExit("키를 입력하지 않아 API를 호출하지 않았습니다.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.openai.com/v1",
    timeout=60,
    max_retries=0,
)


def build_user_prompt(question):
    if question["article_2"] is None:
        return "질문: " + question["question"] + "\n\n--- 기사 ---\n" + question["article_1"]
    return (
        "질문: " + question["question"]
        + "\n\n--- 기사 1 ---\n" + question["article_1"]
        + "\n\n--- 기사 2 ---\n" + question["article_2"]
    )


cloud_questions = [q for q in EVAL_QUESTIONS if q["cloud_비교대상"]]
print(f"Cloud 비교 대상 질문 {len(cloud_questions)}개: "
      + ", ".join(q["id"] for q in cloud_questions))

out = open("cloud_results.jsonl", "w", encoding="utf-8")

for q in cloud_questions:
    print(f"[{q['id']}] {MODEL}에 질문을 보냈습니다. 답변을 기다려 주세요...")
    user_prompt = build_user_prompt(q)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        "provider": "cloud",
        "question_id": q["id"],
        "사례유형": q["사례유형"],
        "repeat_no": 1,  # Cloud는 질문당 1회만 (로컬은 2회 - 반복 수 다름에 유의)
        "question": q["question"],
        "article_1": q["article_1"],
        "article_2": q["article_2"],
    }

    t0 = time.time()
    try:
        response = client.responses.create(
            model=MODEL,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            reasoning={"effort": "none"},
            max_output_tokens=MAX_OUTPUT_TOKENS,
            tools=[],
            tool_choice="none",
            store=False,
        )
        elapsed = time.time() - t0

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        estimated_cost_usd = (
            input_tokens / 1_000_000 * PRICE_PER_MTOK_INPUT
            + output_tokens / 1_000_000 * PRICE_PER_MTOK_OUTPUT
        )

        record.update({
            "status": response.status,  # "completed"가 아니면 중간에 끊겼을 수 있음
            "error_message": None,
            "raw_answer": response.output_text or "",
            "wall_clock_seconds": round(elapsed, 2),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(estimated_cost_usd, 6),
            "cost_note": "공개 단가 기준 추정치, 실제 청구액과 다를 수 있음. "
                         "실제 사용량은 platform.openai.com/usage에서 별도 확인 필요",
        })

        if response.status != "completed":
            print(f"  [주의] 완료 상태가 아닙니다 ({response.status}). 출력이 끊겼을 수 있습니다.")

    except APITimeoutError:
        elapsed = time.time() - t0
        record.update({
            "status": "error",
            "error_message": "APITimeoutError: 응답 대기 시간 초과",
            "raw_answer": None,
            "wall_clock_seconds": round(elapsed, 2),
            "input_tokens": None,
            "output_tokens": None,
            "estimated_cost_usd": None,
            "cost_note": "호출 실패로 비용 산출 불가",
        })
        print("  [오류] 응답 대기 시간이 초과됐습니다.")

    except APIError as error:
        elapsed = time.time() - t0
        status_code = getattr(error, "status_code", "연결 오류")
        record.update({
            "status": "error",
            "error_message": f"APIError: {status_code}",
            "raw_answer": None,
            "wall_clock_seconds": round(elapsed, 2),
            "input_tokens": None,
            "output_tokens": None,
            "estimated_cost_usd": None,
            "cost_note": "호출 실패로 비용 산출 불가",
        })
        print(f"  [오류] API 호출 실패: {status_code}")

    out.write(json.dumps(record, ensure_ascii=False) + "\n")

out.close()
print("\n완료: cloud_results.jsonl 에 결과가 저장되었습니다.")
print("주의: API 키가 이 파일이나 콘솔 출력에 포함되지 않았는지 한 번 더 확인하세요.")