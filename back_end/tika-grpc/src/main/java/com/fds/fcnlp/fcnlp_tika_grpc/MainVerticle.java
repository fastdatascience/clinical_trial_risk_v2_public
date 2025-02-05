package com.fds.fcnlp.fcnlp_tika_grpc;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.sql.Timestamp;
import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

import org.apache.pdfbox.Loader;
import org.apache.pdfbox.text.PDFTextStripper;

import com.fds.fcnlp.fcnlp_tika_grpc.document_parser.DocumentParserResponse;
import com.fds.fcnlp.fcnlp_tika_grpc.document_parser.DocumentParserServiceGrpc;
import com.google.protobuf.ByteString;
import com.google.gson.Gson;

import io.grpc.Server;
import io.vertx.core.AbstractVerticle;
import io.vertx.core.Launcher;
import io.vertx.core.Promise;
import io.vertx.core.impl.logging.Logger;
import io.vertx.core.impl.logging.LoggerFactory;
import io.vertx.grpc.server.GrpcServer;

public class MainVerticle extends AbstractVerticle {

    private Logger logger = LoggerFactory.getLogger(this.getClass());

    /**
     * Takes in a PDF file as binary, extracts the content and sends the content
     * back
     *
     * @throws IOException
     *
     * @apiNote
     *          Tika uses PDFBox under the hood to parse PDFs but the interfaces are
     *          different. Can use PDFBox specially if we are targeting only PDFs
     *          in this handler
     */
    public DocumentParserResponse handleDocumentParseRequest(ByteString file) throws IOException {

        byte[] pdfBytes = file.toByteArray();

        try (var pdfInputStream = new ByteArrayInputStream(pdfBytes); var document = Loader.loadPDF(pdfBytes)) {
            List<String> logs = new ArrayList<String>();

            // * Get metadata
            var info = document.getDocumentInformation();

            Map<String, String> metadata = new HashMap<>();
            metadata.put("title", info.getTitle());
            metadata.put("author", info.getAuthor());
            metadata.put("subject", info.getSubject());
            metadata.put("creator", info.getCreator());
            metadata.put("producer", info.getProducer());
            metadata.put("creation_date", new Timestamp(info.getCreationDate().getTimeInMillis()).toString());
            metadata.put("modification_date", new Timestamp(info.getModificationDate().getTimeInMillis()).toString());
            metadata.put("keywords", info.getKeywords());
            metadata.put("number_of_pages", String.valueOf(document.getNumberOfPages()));

            int numberOfPages = document.getNumberOfPages();

            String parsingFileLogMsg = String.format("Parsing file %s with %s numbers of pages.", info.getTitle(), numberOfPages);
            logger.info(parsingFileLogMsg);
            logs.add(parsingFileLogMsg);

            PDFTextStripper pdfStripper = new PDFTextStripper();

            Map<Integer, String> pages = new HashMap<>();

            for (int page = 1; page <= numberOfPages; ++page) {
                pdfStripper.setStartPage(page);
                pdfStripper.setEndPage(page);

                pages.put(page, pdfStripper.getText(document));
            }

            String parsedFileLogMsg = String.format("Parsed file %s with %s numbers of pages successfully.", info.getTitle(),
                numberOfPages);
            logger.info(parsedFileLogMsg);
            logs.add(parsedFileLogMsg);

            Gson gson = new Gson();
            String logsAsJson = gson.toJson(logs);
            metadata.put("logs", logsAsJson);

            metadata.forEach((key, value) -> metadata.compute(key, (k, v) -> v == null ? "" : v));

            return DocumentParserResponse.newBuilder().putAllPages(pages).putAllMetadata(metadata).build();
        }
    }

    public static void main(String[] args) {
        Launcher.executeCommand("run", MainVerticle.class.getName());
    }

    @Override
    public void start(Promise<Void> startPromise) throws Exception {

        var grpcServer = GrpcServer.server(vertx);

        var server = vertx.createHttpServer();

        grpcServer.callHandler(DocumentParserServiceGrpc.getProcessDocumentMethod(), request -> {
            request.handler(document -> {
                var response = request.response();

                var file = document.getFileContent();

                DocumentParserResponse reply = null;

                try {
                    reply = handleDocumentParseRequest(file);
                } catch (IOException e) {
                    logger.error(e);
                }

                response.end(reply);
            });
        });

        server.requestHandler(grpcServer).listen(8888, http -> {
            if (http.succeeded()) {
                startPromise.complete();
                System.out.println("gRPC server started on port 8888");
            } else {
                startPromise.fail(http.cause());
            }
        });
    }
}
