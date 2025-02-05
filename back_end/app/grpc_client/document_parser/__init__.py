import grpc

from app.grpc_client.document_parser.DocumentParser_pb2 import DocumentParserRequest, DocumentParserResponse
from app.grpc_client.document_parser.DocumentParser_pb2_grpc import DocumentParserServiceStub
from app import config


def process_document(file_contents: bytes) -> DocumentParserResponse:
    with grpc.insecure_channel(config.GRPC_ENDPOINT) as channel:
        stub = DocumentParserServiceStub(channel=channel)

        payload = DocumentParserRequest()
        payload.file_content = file_contents

        response: DocumentParserResponse = stub.processDocument(payload)

        return response
