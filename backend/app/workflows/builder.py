import json
import random
from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


def load_template(name: str) -> dict:
    """Load a workflow template by name."""
    template_path = TEMPLATES_DIR / f"{name}.json"
    with open(template_path) as f:
        return json.load(f)


def build_txt2img_workflow(
    prompt: str,
    negative_prompt: str = "ugly, blurry, low quality",
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    cfg: float = 7.0,
    seed: int | None = None,
    checkpoint: str = "sd_xl_base_1.0.safetensors",
    sampler: str = "euler",
) -> dict:
    """Build a txt2img workflow from parameters."""
    workflow = load_template("basic_txt2img")

    # Set seed (random if not provided)
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    # Update KSampler
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["steps"] = steps
    workflow["3"]["inputs"]["cfg"] = cfg
    workflow["3"]["inputs"]["sampler_name"] = sampler

    # Update checkpoint
    workflow["4"]["inputs"]["ckpt_name"] = checkpoint

    # Update latent size
    workflow["5"]["inputs"]["width"] = width
    workflow["5"]["inputs"]["height"] = height

    # Update prompts
    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt

    return workflow


def parse_technical_parameters(technical_response: str) -> dict:
    """Parse Technical Director's response into workflow parameters."""
    params = {
        "steps": 20,
        "cfg": 7.0,
        "width": 1024,
        "height": 1024,
        "sampler": "euler",
    }

    response_lower = technical_response.lower()

    # Parse steps
    if "steps" in response_lower:
        for word in response_lower.split():
            if word.isdigit() and 10 <= int(word) <= 150:
                params["steps"] = int(word)
                break

    # Parse CFG
    if "cfg" in response_lower:
        for word in response_lower.split():
            try:
                val = float(word)
                if 1 <= val <= 30:
                    params["cfg"] = val
                    break
            except ValueError:
                continue

    # Parse resolution keywords
    if "portrait" in response_lower:
        params["width"] = 768
        params["height"] = 1024
    elif "landscape" in response_lower:
        params["width"] = 1024
        params["height"] = 768
    elif "square" in response_lower:
        params["width"] = 1024
        params["height"] = 1024

    # Parse sampler
    samplers = ["euler", "euler_ancestral", "dpm++", "ddim", "heun"]
    for sampler in samplers:
        if sampler in response_lower:
            params["sampler"] = sampler
            break

    return params
