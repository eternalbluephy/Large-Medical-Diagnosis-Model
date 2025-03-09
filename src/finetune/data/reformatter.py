import re
import json
from pathlib import Path
from typing import Dict, List

RAW_JSON_PATH = Path(__file__).parent.joinpath("CMB-Clin-qa.json")
OUTPUT_PATH = Path(__file__).parent.joinpath("medical.json")
system_prompt = "Role: 医疗诊断助手\n\n## Profile\n- version: 1.0\n- language: 中文\n- description: 我是用户的医疗诊断助手。我会根据用户描述的症状推断出可能的病因和治疗建议。在给出病因后，我会提醒用户\"该诊断结果仅供参考，在任何情况下不能替代专业医师诊断。\"用户提出与医学无关的问题后，我会表示我是医疗诊断大模型，并拒绝回答。\n\n## Skills\n1. 根据用户描述的症状，推断出可能的病因\n2. 在给出病因后，我会提醒用户\"该诊断结果仅供参考，在任何情况下不能替代专业医师诊断。\"\n\n## Rules\n1. 每次在给出病因后，我会提醒用户\"该诊断结果仅供参考，在任何情况下不能替代专业医师诊断。\"。\n3. 根据用户提出的症状合理诊断。\n\n## Workflows\n1. 接收用户提出的症状，合理分析病因，并将所有可能的病因按可能性从高到低输出。\n2. 根据病因，输出给用户的治疗建议\n3. 在给出病因后，提醒用户\"该诊断结果仅供参考，在任何情况下不能替代专业医师诊断。\"\n4. 若用户提出与医学无关的问题，表示自己是医疗诊断大模型，并拒绝回答。\n\n## Init\n我是您的医疗诊断助手。如果您有任何医疗问题或症状，请向我提问。"

def make_conversation(input: str, output: str) -> Dict[str, List[Dict[str, str]]]:
    return {
        "conversation": [{
            "system": system_prompt,
            "input": input,
            "output": output
        }]
    }

def process(text: str) -> str:
    text = re.sub(r'（(\d)）', r'\1.', text)
    text = re.sub(r'[①-⑨]', lambda x: str(ord(x.group()) - ord('①') + 1) + '.', text)
    return text

converations = []

with open(RAW_JSON_PATH, "r", encoding="utf-8") as f:
    ls = json.load(f)
    for item in ls:
        description = item["description"]
        qa_pairs = item["QA_pairs"]
        for qa_pair in qa_pairs:
            input = process(f"{qa_pair['question']}\n{description}")
            output = process(qa_pair["answer"] + "该诊断结果仅供参考，在任何情况下不能替代专业医师诊断。")
            converations.append(make_conversation(input, output))
    
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(json.dumps(converations, ensure_ascii=False))

