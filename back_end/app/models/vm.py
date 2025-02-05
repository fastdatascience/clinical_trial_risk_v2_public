from pydantic import BaseModel, computed_field


class DocumentQueueItem(BaseModel):
    s3_bucket_name: str
    resource_url: str
    user_id: int
    document_id: int
    user_resource_identifier: str

    @computed_field
    @property
    def s3_uri(self) -> str:
        return f"s3://{self.s3_bucket_name}/{self.resource_url}"
