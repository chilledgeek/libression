import io
from typing import Optional, List

import logging

import boto3
import botocore.response
from boto3.resources.base import ServiceResource

S3_BUCKET = "test_photos"
S3_ACCESS_KEY_ID = "minioadmin"
S3_SECRET = "minioadmin"
S3_ENDPOINT_URL = "http://127.0.0.1:9000"
AWS_REGION = "us-east-2"

logger = logging.getLogger(__name__)


class FileIOWrapper:
    def __init__(
            self,
            aws_access_key_id: Optional[str] = None,
            aws_secret_access_key: Optional[str] = None,
            s3_endpoint_url: Optional[str] = None,
    ):
        self.aws_access_key_id = aws_access_key_id if aws_access_key_id is not None else S3_ACCESS_KEY_ID
        self.aws_secret_access_key = aws_secret_access_key if aws_secret_access_key is not None else S3_SECRET
        self.endpoint_url = s3_endpoint_url if s3_endpoint_url is not None else S3_ENDPOINT_URL

        self._inner_s3_client: Optional[ServiceResource] = None

    @property
    def _s3_client(self):
        if self._inner_s3_client is None:
            logger.info("s3_client not yet initiated...initiating now")
            self._inner_s3_client = boto3.client(
                "s3",
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url=self.endpoint_url,
            )
        return self._inner_s3_client

    def list_buckets(self) -> List[str]:
        raw_buckets = self._s3_client.list_buckets()
        return [bucket["Name"] for bucket in raw_buckets["Buckets"]]

    def create_bucket(self, bucket_name: str):
        if bucket_name not in self.list_buckets():
            location = {'LocationConstraint': AWS_REGION}
            self._s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location,
                ACL='public-read-write',
            )

    def delete_bucket(self, bucket_name: str):
        self._s3_client.delete_bucket(
            Bucket=bucket_name,
        )

    def put_object(self,
                   key: str,
                   body: bytes,
                   bucket_name: str) -> None:
        # TODO need feedback?
        file_io = io.BytesIO(body)

        self._s3_client.put_object(
            Body=file_io,
            Bucket=bucket_name,
            Key=key,
            ACL='public-read-write',
        )

    def get_object(self, key: str, bucket_name: str) -> botocore.response.StreamingBody:
        output = self._s3_client.get_object(
            Bucket=bucket_name,
            Key=key,
        )
        if "Body" in output:
            return output["Body"]
        raise FileNotFoundError

    def delete_objects(
            self,
            keys: List[str],
            bucket_name: str
    ):
        self._s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={
                "Objects": [{"Key": key} for key in keys],
                "Quiet": True,
            },
        )

    def list_objects(
            self,
            bucket: str,
            max_keys: int = 1000,
            prefix_filter: Optional[str] = None,
            get_all: bool = False,
    ) -> List[str]:

        response = self._s3_client.list_objects(
            Bucket=bucket,
            **self._kwargs_without_none(MaxKeys=max_keys, Prefix=prefix_filter)
        )

        contents = response.get("Contents")

        if contents is None:
            logger.info("Error with list_objects...returning empty list")
            return []
        else:
            output = [x["Key"] for x in contents]

        if response.get("IsTruncated") and get_all:
            extra_data = self._get_truncated_contents(
                bucket,
                response.get("NextMarker"),
                max_keys,
                prefix_filter,
            )

            output.extend(extra_data)

        return output

    @staticmethod
    def _kwargs_without_none(**kwargs):
        # boto3 doesn't like None kwargs...filter them
        return {k: v for k, v in kwargs.items() if v is not None}

    def _get_truncated_contents(
            self,
            bucket: str,
            next_key: str,
            max_keys: int,
            prefix_filter: str,
    ) -> List[str]:
        output = []
        truncated_flag = True
        while truncated_flag:
            new_contents = self._s3_client.list_objects(
                Bucket=bucket,
                Marker=next_key,
                **self._kwargs_without_none(MaxKeys=max_keys, Prefix=prefix_filter)
            )
            extra_data = [x["Key"] for x in new_contents.get("Contents")]
            output.extend(extra_data)
            next_key = new_contents.get("NextMarker")
            truncated_flag = new_contents.get("IsTruncated")

        return output
