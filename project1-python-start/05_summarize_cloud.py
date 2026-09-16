import json

records = []
f = open("cloud_results.jsonl", encoding="utf-8")
for line in f:
    line = line.strip()
    if line == "":
        continue
    records.append(json.loads(line))
f.close()


def average(values):
    valid = [v for v in values if v is not None]
    if len(valid) == 0:
        return None, 0
    return sum(valid) / len(valid), len(valid)


total = len(records)
success = len([r for r in records if r["status"] == "completed"])

wall_avg, wall_n = average([r["wall_clock_seconds"] for r in records])
input_tok_avg, input_tok_n = average([r["input_tokens"] for r in records])
output_tok_avg, output_tok_n = average([r["output_tokens"] for r in records])
cost_avg, cost_n = average([r["estimated_cost_usd"] for r in records])
cost_sum = sum(v for v in [r["estimated_cost_usd"] for r in records] if v is not None)

print("=" * 60)
print("Cloud (gpt-5.6-luna) 집계 결과")
print("=" * 60)
print(f"호출 성공: {success} / {total}")
print(f"평균 응답 시간: {round(wall_avg, 2) if wall_avg else '없음'}초 (n={wall_n})")
print(f"평균 입력 토큰: {round(input_tok_avg, 1) if input_tok_avg else '없음'} (n={input_tok_n})")
print(f"평균 출력 토큰: {round(output_tok_avg, 1) if output_tok_avg else '없음'} (n={output_tok_n})")
print(f"추정 비용 합계: ${round(cost_sum, 6)} (n={cost_n}건)")
print(f"질문당 평균 추정 비용: ${round(cost_avg, 6) if cost_avg else '없음'}")

summary = {
    "gpt-5.6-luna": {
        "success_count": success,
        "total_attempts": total,
        "wall_clock_seconds_avg": wall_avg,
        "wall_clock_seconds_n": wall_n,
        "input_tokens_avg": input_tok_avg,
        "output_tokens_avg": output_tok_avg,
        "estimated_cost_usd_total": round(cost_sum, 6),
        "estimated_cost_usd_avg_per_call": cost_avg,
        "repeat_no": "1회 (로컬은 2회 - 반복 수 다름에 유의)",
    }
}

out = open("cloud_summary.json", "w", encoding="utf-8")
out.write(json.dumps(summary, ensure_ascii=False, indent=2))
out.close()
print("\n(결과가 cloud_summary.json 파일로도 저장되었습니다)")