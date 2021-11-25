import logging
from typing import List

from resources.file_format import generate_cache_content
from resources.file_io_wrapper import FileIOWrapper

CACHE_BUCKET = "libression-cache"
DATA_BUCKET = "test_photos"
CACHE_SUFFIX = "cache.jpg"

logger = logging.getLogger(__name__)


class FileOrganiser:
    def __init__(
            self
    ):
        self.data_bucket = DATA_BUCKET
        self.cache_bucket = CACHE_BUCKET
        self.file_io = FileIOWrapper()
        self.cache_suffix = CACHE_SUFFIX

    def init_buckets(self):
        existing_buckets = self.file_io.list_buckets()
        for bucket in [self.cache_bucket, self.data_bucket]:
            if bucket not in existing_buckets:
                self.file_io.create_bucket(bucket)

    def list_objects(self):
        return self.file_io.list_objects(self.data_bucket, get_all=True)

    def get_cache_key(self, key: str):
        return f"{key}_{self.cache_suffix}"

    def get_file_s3_url(self, key: str):
        return f"{self.file_io.endpoint_url}/{self.data_bucket}/{key}"

    def save_to_cache(
            self,
            key: str,
            overwrite: bool = True
    ) -> None:
        if (not overwrite) and self.file_io.list_objects(self.cache_bucket, 1, key):
            logger.info(f"key {key} exists...not overwriting")
            return None

        original_content = self.file_io.get_object(key=key, bucket_name=self.data_bucket).read()

        cached_content = generate_cache_content(original_content, key=key)

        self.file_io.put_object(
            key=self.get_cache_key(key),
            body=cached_content,
            bucket_name=self.cache_bucket,
        )

    def load_from_cache(
            self,
            key: str,
    ):
        return self.file_io.get_object(
            key=self.get_cache_key(key),
            bucket_name=self.cache_bucket,
        )

    def ensure_cache(
            self,
            list_of_keys: List[str],
    ):
        # limit calling list_object to only once...
        existing_cache = self.file_io.list_objects(
            bucket=self.cache_bucket,
            get_all=True,
        )

        for key in list_of_keys:
            cache_key = self.get_cache_key(key)
            if cache_key not in existing_cache:
                self.save_to_cache(key)

