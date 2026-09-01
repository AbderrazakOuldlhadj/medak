import sys
import os

sys.path.append(r'C:\Users\msipc\AppData\Roaming\Python\Python310\site-packages')
sys.path.append(os.path.dirname(__file__))
sys.stdout.reconfigure(encoding='utf-8')

import google_sheets_mcp as mcp_mod

SPREADSHEET_ID = "1oI09pLLMrCaoJokOB_gvIQQP7pObCE3_M7_LiyWf8rc"

headers = [
    ["Google AI Models Comparison - Intelligence, Speed & Pricing"],
    ["Generated on: 2026-08-02"],
    [],
    [
        "Model Name",
        "Category",
        "Intelligence (1-10)",
        "Speed Tier",
        "Tokens / Sec",
        "Context Window",
        "Input Price / 1M Tokens ($)",
        "Output Price / 1M Tokens ($)",
        "Key Strengths & Use Cases"
    ]
]

data = [
    [
        "Gemini 2.5 Pro",
        "Flagship Multimodal",
        9.8,
        "Moderate",
        "75 t/s",
        "2,000,000",
        "$1.25",
        "$5.00",
        "Top-tier reasoning, complex coding, massive context analysis, multimodal QA"
    ],
    [
        "Gemini 2.0 Flash Thinking",
        "Reasoning / Math",
        9.6,
        "Fast",
        "120 t/s",
        "1,000,000",
        "$0.10",
        "$0.40",
        "Advanced step-by-step reasoning, mathematical problem solving, chain of thought"
    ],
    [
        "Gemini 2.5 Flash",
        "Balanced / Fast",
        8.9,
        "Very Fast",
        "200 t/s",
        "1,000,000",
        "$0.075",
        "$0.30",
        "High performance at low cost, audio/video analysis, chat agents, high volume"
    ],
    [
        "Gemini 1.5 Flash-8B",
        "Ultra Lightweight",
        7.9,
        "Ultra Fast",
        "320 t/s",
        "1,000,000",
        "$0.0375",
        "$0.15",
        "High throughput tasks, simple text processing, real-time response apps"
    ],
    [
        "Gemini 1.5 Pro",
        "Long Context Pro",
        9.3,
        "Moderate",
        "60 t/s",
        "2,000,000",
        "$1.25",
        "$5.00",
        "Complex document understanding, video analysis up to 1 hour, codebases"
    ],
    [
        "Gemma 2 (27B)",
        "Open Weights",
        8.6,
        "Custom / High",
        "N/A (Self-Hosted)",
        "8,192",
        "Free (Open Source)",
        "Free (Open Source)",
        "Self-hosted enterprise deployment, privacy, customizable open weights"
    ],
    [
        "Gemma 2 (9B)",
        "Open Weights",
        7.8,
        "Custom / Fast",
        "N/A (Self-Hosted)",
        "8,192",
        "Free (Open Source)",
        "Free (Open Source)",
        "Lightweight self-hosting, fine-tuning, developer experimentation"
    ],
    [
        "Gemma 2 (2B)",
        "On-Device / Mobile",
        6.9,
        "Instant (Local)",
        "N/A (Self-Hosted)",
        "8,192",
        "Free (Open Source)",
        "Free (Open Source)",
        "Edge computing, mobile app integration, zero-latency offline generation"
    ],
    [
        "Imagen 3",
        "Image Generation",
        9.5,
        "Fast (~4 sec)",
        "N/A",
        "Prompt Based",
        "$0.03 / image",
        "N/A",
        "Photorealistic image generation, typography rendering, detailed art"
    ],
    [
        "Veo 2",
        "Video Generation",
        9.6,
        "Batch Processing",
        "N/A",
        "Prompt / Image",
        "Per generation",
        "N/A",
        "1080p high definition video synthesis, consistent motion, visual storytelling"
    ]
]

def populate():
    all_rows = headers + data
    res = mcp_mod.update_spreadsheet_range(SPREADSHEET_ID, "Sheet1!A1:I14", all_rows)
    print(res)

if __name__ == '__main__':
    populate()
