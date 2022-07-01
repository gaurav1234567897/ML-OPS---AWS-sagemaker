import boto3
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class ModelSnapShotHandler:
    def __init__(self, region=None):
        self.region = boto3.Session().region_name
        if self.region is None:
            self.region = region
        self.cc_client = boto3.client('codecommit', region_name="us-west-2")
        self.sm_client = boto3.client('sagemaker', region_name=self.region)

    def get_model_package_arn(self, model_packages):
        return model_packages[0].get("ModelPackageArn")

    def get_model_registry_snapshot(self, model_name):
        # list model packages
        model_packages = self.sm_client.list_model_packages(
            ModelPackageGroupName=model_name,
            ModelApprovalStatus="Approved",
            SortBy="CreationTime",
            SortOrder="Descending",
            MaxResults=1
        ).get("ModelPackageSummaryList")
        logger.info(f"model_packages: {model_packages}")

        # find model package arn
        model_package_arn = self.get_model_package_arn(model_packages)
        logger.info(f"model package arn: {model_package_arn}")

        # build model info json
        model_info = {
            "model": model_name,
            "model_package_arn": model_package_arn
        }

        return model_info

    def get_head_commit(self, repository_name, branch_name):
        try:
            response = self.cc_client.get_branch(
                repositoryName=repository_name,
                branchName=branch_name
            )
            return response["branch"]["commitId"]
        except self.cc_client.exceptions.BranchDoesNotExistException:
            return None

    def write_commit(self, repository_name, branch_name, model_info_input, model_name):

        head_commit = self.get_head_commit(repository_name, branch_name)

        get_file_kwargs = {
            "repositoryName" : repository_name,
            "commitSpecifier" : head_commit,
            "filePath" : f"configuration/region_snapshot/{self.region}.json"
        }
        try:
            get_file_content = self.cc_client.get_file(**get_file_kwargs)['fileContent']
        except:
            get_file_content = None

        get_file_content_decoded = json.loads(get_file_content or '[]')

        put_file_content = []
        model_exist = False

        for model_params in get_file_content_decoded:
            if model_params['model'] == model_info_input['model']:
                put_file_content.append(model_info_input)
                model_exist = True
            else:
                put_file_content.append(model_params)

        if not model_exist:
            put_file_content.append(model_info_input)

        put_file_content_encoded = json.dumps(put_file_content, indent = 4, sort_keys = True).encode("utf-8")

        try:
            put_file_kwargs = {
                "repositoryName": repository_name,
                "branchName": branch_name,
                "fileContent": put_file_content_encoded,
                "filePath": f"configuration/region_snapshot/{self.region}.json",
                "commitMessage": f"Updating model {model_name} registries for region: {self.region}",
                "name": "cron-user"
            }
            if head_commit is not None:
                put_file_kwargs["parentCommitId"] = head_commit
            self.cc_client.put_file(**put_file_kwargs)
            logger.info("Model registry snapshot was successfully committed")
        except self.cc_client.exceptions.SameFileContentException:
            logger.error("Same file content encountered")

    def write_model_details(self, event, context):
        model_name = event.get("model_name")
        repository_name = event.get("repository_name")
        branch_name = event.get("branch_name")

        logger.info(
            f"model_name: {model_name}, "
            f"repository_name: {repository_name}, "
            f"branch_name: {branch_name}")

        model_registry_snapshot = self.get_model_registry_snapshot(model_name)

        self.write_commit(repository_name, branch_name, model_registry_snapshot, model_name)

        return {
            "statusCode": 200,
            "body": model_registry_snapshot
        }


def lambda_handler(event, context):
    return ModelSnapShotHandler().write_model_details(event, context)