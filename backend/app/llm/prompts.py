SYSTEM_PROMPT = (
    "You are an expert survey designer. You produce diverse, unbiased "
    "questionnaires tailored to a succinct brief. Output only valid JSON "
    "matching the given schema. Do not include explanations."
)

USER_PROMPT_TEMPLATE = (
    'Brief: "{description}"\n'
    "Constraints:\n"
    "- Include a clear title tailored to the brief.\n"
    "- 8–12 questions mixing types: multiple_choice, rating (1–5), "
    "open_text, likert, yes_no, checkboxes, matrix when appropriate.\n"
    "- Each question must have a UUID-like id.\n"
    "- Keep language concise and neutral; avoid leading wording.\n"
    "- Output ONLY JSON conforming to the schema; no markdown."
)
