import requests
import sys
import json

API_URL = "http://127.0.0.1:8000/ats-api/analyze/files"

def analyze(resume_path: str, jd_path: str = None):
    print("\nAnalyzing... please wait\n")

    files = {"resume_file": (resume_path, open(resume_path, "rb"), "application/pdf")}
    if jd_path:
        files["jd_file"] = (jd_path, open(jd_path, "rb"), "application/pdf")

    try:
        response = requests.post(API_URL, files=files)
    finally:
        for _, (_, fh, _) in files.items():
            fh.close()

    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    payload = response.json()
    data = payload["data"]
    mode = payload.get("meta", {}).get("mode", "resume_vs_jd")
    mode_label = "Resume vs Job Description" if mode == "resume_vs_jd" else "Resume Only (general ATS check)"

    # ATS Score
    score = data["ats_score"]
    rating = data["rating"]
    bar = "█" * (score // 5) + "░" * (20 - score // 5)
    print(f"{'='*50}")
    print(f"  MODE: {mode_label}")
    print(f"  ATS SCORE:  {score}/100  [{rating}]")
    print(f"  [{bar}]")
    print(f"{'='*50}\n") 

    # Summary
    print(f"SUMMARY\n  {data['summary']}\n")

    # Stats
    s = data["stats"]
    print("STATS")
    print(f"  Keywords matched   : {s['matched_keywords']} / {s['total_keywords']}")
    print(f"  Experience match   : {s['years_experience_match']}")
    print(f"  Education match    : {s['education_match']}\n")

    # Category Scores
    print("CATEGORY BREAKDOWN")
    for cat in data["categories"]:
        bar = "█" * (cat["score"] // 5) + "░" * (20 - cat["score"] // 5)
        print(f"  {cat['name']:<18} {cat['score']:>3}%  [{bar}]")
        print(f"  {'':18} ↳ {cat['note']}")
    print()

    # Skills
    print("MATCHED SKILLS")
    print("  " + ",  ".join(data["skills"]["matched"]) if data["skills"]["matched"] else "  None")
    print()

    print("PARTIAL MATCH SKILLS")
    print("  " + ",  ".join(data["skills"]["partial"]) if data["skills"]["partial"] else "  None")
    print()

    print("MISSING SKILLS")
    print("  " + ",  ".join(data["skills"]["missing"]) if data["skills"]["missing"] else "  None")
    print()

    # Action Plan
    print("ACTION PLAN")
    for i, tip in enumerate(data["action_plan"], 1):
        pri = tip["priority"]
        icon = "🔴" if pri == "High" else "🟡" if pri == "Medium" else "🟢"
        print(f"  {i}. {icon} [{pri}] {tip['action']}")
        print(f"       → {tip['impact']}")
    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        # 2 == resume only
        # 3 == resume + job description
        print("Usage: python cli.py <resume.pdf> [job_description.pdf]")
        print("Example (with JD):    python cli.py resume.pdf job_description.pdf")
        print("Example (resume only): python cli.py resume.pdf")
        sys.exit(1)

    resume_arg = sys.argv[1]
    jd_arg = sys.argv[2] if len(sys.argv) == 3 else None
    analyze(resume_arg, jd_arg)