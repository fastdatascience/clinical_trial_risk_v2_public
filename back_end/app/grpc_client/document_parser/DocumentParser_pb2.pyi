from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DocumentParserRequest(_message.Message):
    __slots__ = ("file_content",)
    FILE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    file_content: bytes
    def __init__(self, file_content: _Optional[bytes] = ...) -> None: ...

class DocumentParserResponse(_message.Message):
    __slots__ = ("pages", "metadata")
    class PagesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: str
        def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PAGES_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    pages: _containers.ScalarMap[int, str]
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, pages: _Optional[_Mapping[int, str]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...
