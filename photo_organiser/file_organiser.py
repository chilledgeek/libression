import logging
from typing import List, Tuple
import concurrent.futures
from resources.file_formatting import generate_cache_content
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
        return f"{self.file_io.endpoint_url}{self.get_file_s3_canonical_uri(key)}"

    def get_file_s3_canonical_uri(self, key: str):
        return f"/{self.data_bucket}/{key}"

    def save_to_cache(self, key: str):

        original_content = self.file_io.get_object_body(key=key, bucket_name=self.data_bucket)
        cached_content = generate_cache_content(original_content, key=key)

        self.file_io.put_object(
            key=self.get_cache_key(key),
            body=cached_content,
            bucket_name=self.cache_bucket,
        )
        return cached_content

    def load_from_cache(
            self,
            key: str,
    ):
        return self.file_io.get_object_body(
            key=self.get_cache_key(key),
            bucket_name=self.cache_bucket,
        )

    def load_from_data_bucket(
            self,
            key: str,
    ):
        return self.file_io.get_object(
            key=key,
            bucket_name=self.data_bucket,
        )

    def ensure_cache_bulk(
            self,
            list_of_keys: List[str],
            overwrite: bool = False,
    ):
        # limit calling list_object to only once...
        existing_cache = self.file_io.list_objects(
            bucket=self.cache_bucket,
            get_all=True,
        )

        if overwrite:
            cache_to_render = existing_cache  # overwrite everything!
        else:
            cache_to_render = [
                key for key in list_of_keys
                if self.get_cache_key(key) not in existing_cache
            ]

        logger.info(f"checking/generating cache for {len(cache_to_render)} entities...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
            cache_future = [executor.submit(self.save_to_cache, key)
                            for key in cache_to_render]

        logger.info(f"completed checking/generating cache for {len(cache_to_render)} entities...")

        # try dict, if using results to generate phash and updating db?
        return [x.result() for x in cache_future]

    def get_rel_dirs_and_content(
            self,
            get_subdir_content: bool,
            show_hidden_content: bool,
            rel_dir_no_slash: str = "",
    ) -> Tuple[List[str], List[str]]:

        dirs, file_keys = self.file_io.get_subdirs_and_content(
            self.data_bucket,
            get_subdir_content=get_subdir_content,
            rel_dir_no_slash=rel_dir_no_slash,
        )

        if len(rel_dir_no_slash.split("/")) > 1:
            dirs.insert(0, "/".join(rel_dir_no_slash.split("/")[:-1]))

        if not show_hidden_content:
            file_keys = [
                key for key in file_keys
                if not key.split("/")[-1].startswith(".")
                   and key.startswith(rel_dir_no_slash)
            ]

        return dirs, file_keys

