import os
import sys

import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor

# Standard fallback for the local models directory if running directly
MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models"))
MODEL_NAME = "baidu--Unlimited-OCR"  # robust downloader replaces / with --


def main():
    model_path = os.path.join(MODELS_DIR, MODEL_NAME)

    if not os.path.exists(model_path):
        print(f"[ERROR] Model not found at {model_path}")
        print("Please run `python download_all_models.py` first.")
        sys.exit(1)

    print(f"Loading Baidu Unlimited-OCR from: {model_path}")
    print("Initializing in fp16. This requires ~6-7 GB of GPU VRAM.")

    try:
        # Some custom models from Baidu require trust_remote_code
        processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)

        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        print("[SUCCESS] Model loaded successfully.")
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] Failed to load the model: {e}")
        sys.exit(1)

    # For testing, we just check if an image path was provided
    if len(sys.argv) < 2:
        print("\nUsage: python scripts/run_unlimited_ocr.py <path_to_image>")
        print("Model loaded successfully. Exiting since no image was provided.")
        sys.exit(0)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"[ERROR] Image not found: {image_path}")
        sys.exit(1)

    try:
        print(f"\nProcessing image: {image_path}")
        image = Image.open(image_path).convert("RGB")

        # Standard instruction for OCR models
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {
                        "type": "text",
                        "text": "Extract all text from this image and preserve markdown formatting.",
                    },
                ],
            }
        ]

        # This is the standard API for modern Transformers VLMs (Qwen2-VL, DeepSeek, etc)
        text_prompt = processor.apply_chat_template(
            messages, add_generation_prompt=True
        )
        inputs = processor(
            text=[text_prompt], images=[image], padding=True, return_tensors="pt"
        )
        inputs = inputs.to(model.device)

        print("Running inference...")
        with torch.no_grad():
            output_ids = model.generate(**inputs, max_new_tokens=2048)

        generated_ids = [
            output_ids[i][len(inputs.input_ids[i]) :] for i in range(len(output_ids))
        ]

        result_text = processor.batch_decode(
            generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )[0]

        print("\n--- OCR RESULT ---\n")
        print(result_text)
        print("\n------------------\n")

    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] Inference failed: {e}")


if __name__ == "__main__":
    main()
