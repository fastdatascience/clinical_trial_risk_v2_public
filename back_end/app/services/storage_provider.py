import os
from datetime import UTC, datetime, timedelta
from typing import Literal, cast

import boto3
from azure.core.paging import ItemPaged
from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas, BlobProperties
from botocore.client import BaseClient
from mypy_boto3_s3 import S3Client

from app import config
from app.utils import split_list_into_chunks
from app.security import encode_sha256


class StorageProvider:
    __storage_client: BaseClient | BlobServiceClient

    def __init__(self):
        self.provider: Literal["s3"] | Literal["azure"] = config.STORAGE_PROVIDER

        match self.provider:
            case "s3":
                self.__setup_s3()
            case "azure":
                self.__setup_azure()

    def __setup_s3(self):
        aws_access_key = os.environ.get("AWS_ACCESS_KEY")
        if not aws_access_key:
            raise ValueError("AWS_ACCESS_KEY not set")

        aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        if not aws_secret_access_key:
            raise ValueError("AWS_SECRET_ACCESS_KEY not set")

        self.__storage_client = boto3.client(service_name="s3", aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)

    def __setup_azure(self):
        azure_connection_string = os.getenv("AZURE_CONNECTION_STRING")
        if not azure_connection_string:
            raise ValueError("AZURE_CONNECTION_STRING not set")

        self.__storage_client = BlobServiceClient.from_connection_string(azure_connection_string)

    def file_exists(self, file_name: str) -> bool:
        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)
                try:
                    s3_client.get_object(Bucket=config.BUCKET_OR_CONTAINER_NAME, Key=file_name)
                    return True
                except s3_client.exceptions.NoSuchKey:
                    return False
            case ("azure", client) if isinstance(client, BlobServiceClient):
                blob_service_client = cast(BlobServiceClient, client)
                blob_client = blob_service_client.get_blob_client(container=config.BUCKET_OR_CONTAINER_NAME, blob=file_name)
                return blob_client.exists()
            case _:
                raise ValueError("Unsupported storage provider")

    def get_file(self, file_name: str) -> bytes:
        file_name = file_name.rstrip("/").lstrip("/")
        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)
                response = s3_client.get_object(Bucket=config.BUCKET_OR_CONTAINER_NAME, Key=file_name)
                return response["Body"].read()
            case ("azure", client) if isinstance(client, BlobServiceClient):
                blob_client = client.get_blob_client(container=config.BUCKET_OR_CONTAINER_NAME, blob=file_name)
                return blob_client.download_blob().readall()
            case _:
                raise ValueError("Unsupported storage provider")

    def put_file(self, file_name: str, data: bytes, content_type: str = ""):
        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)
                s3_client.put_object(Bucket=config.BUCKET_OR_CONTAINER_NAME, Key=file_name, Body=data, ContentType=content_type)
            case ("azure", client) if isinstance(client, BlobServiceClient):
                blob_client = client.get_blob_client(container=config.BUCKET_OR_CONTAINER_NAME, blob=file_name)
                blob_client.upload_blob(data, overwrite=True)
            case _:
                raise ValueError("Unsupported storage provider")

    def delete_file(self, file_name: str):
        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)
                s3_client.delete_object(Bucket=config.BUCKET_OR_CONTAINER_NAME, Key=file_name)
            case ("azure", client) if isinstance(client, BlobServiceClient):
                blob_client = client.get_blob_client(container=config.BUCKET_OR_CONTAINER_NAME, blob=file_name)
                blob_client.delete_blob()
            case _:
                raise ValueError("Unsupported storage provider")

    def list_files_under_path(self, path: str) -> list[str]:
        if not path.endswith("/"):
            path = f"{path}/"

        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)

                result = s3_client.list_objects(Bucket=config.BUCKET_OR_CONTAINER_NAME, Prefix=path, Delimiter='/')
                file_names = [x["Key"] for x in result["Contents"]]

                return file_names
            case ("azure", client) if isinstance(client, BlobServiceClient):
                blob_service_client = cast(BlobServiceClient, client)
                container_client = blob_service_client.get_container_client(container=config.BUCKET_OR_CONTAINER_NAME)

                blob_properties: ItemPaged[BlobProperties] = container_client.list_blobs(name_starts_with=path)
                file_names =  [x.name for x in blob_properties]

                return file_names
            case _:
                raise ValueError("Unsupported storage provider")

    def delete_files(self, file_names: list[str]):
        if not file_names:
            return

        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)

                # Up to 1000 objects can be deleted per delete_objects call
                chunks = split_list_into_chunks(l=file_names, n=1000)
                for chunk in chunks:
                    s3_client.delete_objects(
                        Bucket=config.BUCKET_OR_CONTAINER_NAME,
                        Delete={"Objects": [{"Key": x} for x in chunk]}
                    )
            case ("azure", client) if isinstance(client, BlobServiceClient):
                blob_service_client = cast(BlobServiceClient, client)
                container_client = blob_service_client.get_container_client(container=config.BUCKET_OR_CONTAINER_NAME)

                # Up to 256 blobs can be deleted per delete_blobs call
                chunks = split_list_into_chunks(l=file_names, n=256)
                for chunk in chunks:
                    container_client.delete_blobs(*chunk)
            case _:
                raise ValueError("Unsupported storage provider")

    def get_public_url(self, file_name: str) -> str:
        file_name = file_name.rstrip("/").lstrip("/")
        match (self.provider, self.__storage_client):
            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)
                return s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": config.BUCKET_OR_CONTAINER_NAME, "Key": file_name},
                    ExpiresIn=3600,
                )
            case ("azure", client) if isinstance(client, BlobServiceClient):
                cd_base_url = os.environ.get("CDN_BASE_URL")
                if not cd_base_url:
                    raise ValueError("CDN_BASE_URL not set")
                return f"{cd_base_url}/{config.BUCKET_OR_CONTAINER_NAME}/{config.CDN_BUCKET_OR_CONTAINER_BASE_PATH}/{file_name}"
            case _:
                raise ValueError("Unsupported storage provider")

    def get_internal_cdn_url(self, user_id: int, object_id: int, expiry_seconds=60) -> str:
        """
        Generate a signed time based url using internal cdn

            Args:
                user_id (int): User id
                object_id (str): Id for the document or object
                expiry_seconds (int): The number of seconds until the URL expires

        """
        # * Calculate expiration time
        expiry_time = int((datetime.now(UTC) + timedelta(seconds=expiry_seconds)).timestamp())

        signature = encode_sha256(source_data=f"{user_id}::{expiry_time}")
        return f"{config.SERVER_URL}{config.API_V1_STR}/documents/cdn/{object_id}/{signature}"

    def generate_signed_url(self, file_name: str, expiry_seconds: int = 3600) -> str:
        """
        Generates a signed URL for Azure CDN or S3

        Args:
            file_name (str): The name of the file to generate the URL for
            expiry_seconds (int): The number of seconds until the URL expires

        Returns:
            str: The signed URL

        Raises:
            ValueError: If the storage provider is unsupported or required environment variables are missing
        """
        file_name = file_name.rstrip("/").lstrip("/")
        match (self.provider, self.__storage_client):
            case ("azure", client) if isinstance(client, BlobServiceClient):
                cdn_base_url = os.environ.get("CDN_BASE_URL")
                if not cdn_base_url:
                    raise ValueError("CDN_BASE_URL not set")

                sas_token = generate_blob_sas(
                    account_name=str(client.account_name),
                    container_name=config.BUCKET_OR_CONTAINER_NAME,
                    blob_name=file_name,
                    account_key=client.credential.account_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.now(UTC) + timedelta(seconds=expiry_seconds),
                    protocol="https",
                    cache_control="no-cache",
                    content_disposition="inline",
                    content_encoding="utf-8",
                    content_language="en-US",
                )

                return f"{cdn_base_url}/{config.BUCKET_OR_CONTAINER_NAME}/{config.CDN_BUCKET_OR_CONTAINER_BASE_PATH}/{file_name}?{sas_token}"

            case ("s3", client) if isinstance(client, BaseClient):
                s3_client = cast(S3Client, client)
                return s3_client.generate_presigned_url("get_object", Params={"Bucket": config.BUCKET_OR_CONTAINER_NAME, "Key": file_name}, ExpiresIn=expiry_seconds)

            case _:
                raise ValueError("Unsupported storage provider")
