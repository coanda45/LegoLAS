from roboflow import Roboflow
from segment_anything import sam_model_registry
import torch


def load_model_RF(api_key: str, project_id: str, version: int):
    """Load a model from Roboflow"""
    rf = Roboflow(api_key=api_key)
    project = rf.workspace().project(project_id)
    model = project.version(version).model

    return model


def load_SAM():
    """Load the ligthest Segment-anything model from META"""
    weights = "resources/SAM_weights/sam_vit_b_01ec64.pth"  # trained weights; get them online (~350 Mb)
    model_type = "vit_b"
    device = "cuda" if torch.cuda.is_available() else "cpu"  # cuda = GPU
    print(f"SAM: GPU will {'' if device=='cuda' else 'NOT '}be used")
    model = sam_model_registry[model_type](checkpoint=weights)
    model.to(device=device)

    return model
