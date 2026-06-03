import json
from dataclasses import dataclass, field
from typing import Any, Literal

import torch
from torch.nn import Module
from transformers import pipeline

from config import MODELS_CONFIG


@dataclass
class ModelConfig:
    model_name: Literal["ner", "zero-shot"]
    parameters: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load_config(cls, model_name: Literal["ner", "zero-shot"]) -> "ModelConfig":
        with open(MODELS_CONFIG, "r", encoding="utf-8") as file:
            raw_config = json.load(file)

        return cls(
            model_name=model_name,
            parameters=raw_config.get(model_name, {})
        )


class Model(Module):
    def __init__(self, config: ModelConfig, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.config = config
        self.pipeline = self._build_pipeline()

    def _build_pipeline(self):
        device = self.config.parameters.get("device")
        if device is None:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_path = self.config.parameters.get("model_path")
        if self.config.model_name == "zero-shot":
            return pipeline(
                task="zero-shot-classification",
                model=model_path,
                device=device
            )

        if self.config.model_name =="ner":
            agg_strategy = self.config.parameters.get("aggregation_strategy", "simple")
            return pipeline(
                task="token-classification",
                model=model_path,
                aggregation_strategy=agg_strategy,
                device=device
            )

        raise NotImplementedError

    def forward(self, text: str, **kwargs):
        if self.config.model_name == "zero-shot":
            labels = self.config.parameters.get("categories")
            if "candidate_labels" not in kwargs:
                    kwargs["candidate_labels"] = labels

        return self.pipeline(text, **kwargs)


zero_shot_model = Model(ModelConfig.load_config("zero-shot"))
ner_model = Model(ModelConfig.load_config("ner"))


def run_zero_shot(text: str) -> dict | None:
    try:
        predict = zero_shot_model(text)
    except ValueError: #In case if no text included
        return None
    del predict["sequence"]
    return predict

def run_ner(text: str) -> dict | None:
    try:
        predict = ner_model(text)
    except ValueError: #In case if no text included
        return None
    for entity in predict:
        entity["score"] = float(entity["score"])
    return {"predict": predict}
