
from roboflow import Roboflow


def load_model(api_key: str,
               project_id: str,
               version: int):

    rf = Roboflow(api_key=api_key)
    project = rf.workspace().project(project_id)
    model = project.version(version).model

    return model
