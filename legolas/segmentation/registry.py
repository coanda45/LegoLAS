from pathlib import Path
import requests

from roboflow import Roboflow
from segment_anything import sam_model_registry
import torch

def load_model_RF(api_key: str, project_id: str, version: int):
    """Load a model from Roboflow"""
    rf = Roboflow(api_key=api_key)
    project = rf.workspace().project(project_id)
    model = project.version(version).model
    print(f"RF model = {project_id} v{version}")

    return model


def load_SAM():
    """Load the lightest Segment-anything model from META
    Download the Vit-B SAM model checkpoint if not in /tmp/ (~350 Mb). See
    https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints
    """
    print("initializing SAM model...")
    weights_path = "/tmp/sam_vit_b_01ec64.pth"  # trained weights
    if not Path(weights_path).is_file():
        print("  downloading SAM weights...", end="", flush=True)
        try:
            url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(weights_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(" done!")
            if Path(weights_path).stat().st_size < 100_000_000:
                raise ValueError(f"Downloaded file is too small — likely corrupted. Delete {weights_path} and try again.")

        except Exception as e:
            print(e)
            print("  /!\ Cound not download SAM weights. You need to download the Vit-B SAM model checkpoint here:\n" \
            + "  https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints\n" \
            + "  and store sam_vit_b_01ec64.pth in /tmp/")
            return None
    else:
        print(f"  SAM weights found here: {weights_path}")

    model_type = "vit_b"
    device = "cuda" if torch.cuda.is_available() else "cpu"  # cuda = GPU
    print(f"SAM: GPU will {'' if device=='cuda' else 'NOT '}be used")
    model = sam_model_registry[model_type](checkpoint=weights_path)
    model.to(device=device)

    return model
