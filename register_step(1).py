from typing import Union, List

from sagemaker import ModelMetrics, MetricsSource, Model, PipelineModel
from sagemaker.workflow.step_collections import RegisterModel

APPROVAL_STATUS = "PendingManualApproval"
APPLICATION_JSON = "application/json"


def get_register_step(
    pipeline_name: str,
    step_name: str,
    instance_type: str,
    model: Union[Model, PipelineModel],
    content_types: List[str],
    response_types: List[str],
    model_metrics_location: str = None
) -> RegisterModel:
    return RegisterModel(
        name=step_name,
        model=model,
        content_types=content_types,
        response_types=response_types,
        inference_instances=[instance_type],
        transform_instances=[instance_type],
        model_package_group_name=pipeline_name,
        approval_status=APPROVAL_STATUS,
        model_metrics=ModelMetrics(
            model_statistics=MetricsSource(
                s3_uri=model_metrics_location,
                content_type=APPLICATION_JSON)) if model_metrics_location is not None else None)
