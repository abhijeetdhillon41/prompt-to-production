# skills.md

skills:
  - name: classify_complaint
    description: Classifies a single citizen complaint into category, priority, reason, and review flag.
    input: One complaint row with a description text field (string).
    output: "category (one of: Pothole, Flooding, Streetlight, Waste, Noise, Road Damage, Heritage Damage, Heat Hazard, Drain Blockage, Other), priority (Urgent, Standard, or Low), reason (one sentence citing specific words from the description), flag (NEEDS_REVIEW or blank)."
    error_handling: "If the description is empty or does not clearly map to a single category, set category to Other and flag to NEEDS_REVIEW. Priority is Urgent if any severity keyword (injury, child, school, hospital, ambulance, fire, hazard, fell, collapse) appears in the description (case-insensitive), otherwise Standard or Low."

  - name: batch_classify
    description: Reads an input CSV, applies classify_complaint to each row, and writes the results to an output CSV.
    input: "Path to input CSV file (--input) containing complaint rows with a description column."
    output: "Path to output CSV file (--output) with original columns plus category, priority, reason, and flag columns."
    error_handling: "If the input file is missing or unreadable, exit with an error message. Rows that fail classification are written with category Other and flag NEEDS_REVIEW."
