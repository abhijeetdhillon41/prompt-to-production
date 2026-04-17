"""
UC-0A — Complaint Classifier
Classifies citizen complaints by category, priority, reason, and review flag.
"""
import argparse
import csv
import re

CATEGORIES = [
    "Pothole", "Flooding", "Streetlight", "Waste", "Noise",
    "Road Damage", "Heritage Damage", "Heat Hazard", "Drain Blockage", "Other"
]

SEVERITY_KEYWORDS = [
    "injury", "child", "school", "hospital", "ambulance",
    "fire", "hazard", "fell", "collapse"
]

CATEGORY_KEYWORDS = {
    "Pothole": ["pothole"],
    "Flooding": ["flood", "flooded", "flooding", "waterlog", "submerge", "stranded"],
    "Streetlight": ["streetlight", "street light", "lights out", "light out", "flickering", "sparking"],
    "Waste": ["garbage", "waste", "rubbish", "trash", "dumped", "overflowing", "dead animal", "not removed"],
    "Noise": ["noise", "loud", "music", "midnight", "decibel"],
    "Road Damage": ["road surface", "cracked", "sinking", "broken", "upturned", "footpath", "manhole", "tiles"],
    "Heritage Damage": ["heritage"],
    "Heat Hazard": ["heat", "heatwave", "sunstroke"],
    "Drain Blockage": ["drain", "blocked drain", "drain block"],
    "Flooding": ["flood", "flooded", "flooding"],
}


def _match_category(desc_lower: str) -> tuple:
    """Returns (category, is_ambiguous). Checks keywords against description."""
    matches = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in desc_lower:
                if cat not in matches:
                    matches.append(cat)
                break
    if len(matches) == 1:
        return matches[0], False
    if len(matches) > 1:
        return matches[0], True
    return "Other", True


def _check_urgent(desc_lower: str) -> bool:
    return any(kw in desc_lower for kw in SEVERITY_KEYWORDS)


def _build_reason(category: str, priority: str, desc_lower: str) -> str:
    cited = []
    all_kw = CATEGORY_KEYWORDS.get(category, []) + (SEVERITY_KEYWORDS if priority == "Urgent" else [])
    for kw in all_kw:
        if kw in desc_lower and kw not in cited:
            cited.append(kw)
    if cited:
        return f"Description contains {', '.join(repr(w) for w in cited)} indicating {category} with {priority} priority."
    return f"Classified as {category} based on overall description context."


def classify_complaint(row: dict) -> dict:
    """
    Classify a single complaint row.
    Returns: dict with keys: complaint_id, category, priority, reason, flag
    """
    desc = row.get("description", "")
    desc_lower = desc.lower()

    category, ambiguous = _match_category(desc_lower)
    priority = "Urgent" if _check_urgent(desc_lower) else "Standard"
    if priority == "Standard" and category == "Other":
        priority = "Low"
    reason = _build_reason(category, priority, desc_lower)
    flag = "NEEDS_REVIEW" if ambiguous else ""

    return {
        "complaint_id": row.get("complaint_id", ""),
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify each row, write results CSV.
    """
    results = []
    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                results.append(classify_complaint(row))
            except Exception:
                results.append({
                    "complaint_id": row.get("complaint_id", ""),
                    "category": "Other",
                    "priority": "Low",
                    "reason": "Classification failed for this row.",
                    "flag": "NEEDS_REVIEW",
                })

    fieldnames = ["complaint_id", "category", "priority", "reason", "flag"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UC-0A Complaint Classifier")
    parser.add_argument("--input",  required=True, help="Path to test_[city].csv")
    parser.add_argument("--output", required=True, help="Path to write results CSV")
    args = parser.parse_args()
    batch_classify(args.input, args.output)
    print(f"Done. Results written to {args.output}")
