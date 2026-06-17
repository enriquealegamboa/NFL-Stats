package com.nflstats.backend.error;

import jakarta.servlet.http.HttpServletRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import java.util.List;
import java.util.Map;

/**
 * Central error handler — the Spring equivalent of the Express
 * {@code middleware/errorHandler.ts}. Every error is rendered as the standard
 * {@link ErrorEnvelope}; unknown errors are logged server-side and returned as
 * an opaque 500 (no stack trace leaks to the client).
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    /** Expected, client-facing errors carry their own code/status/details. */
    @ExceptionHandler(AppException.class)
    public ResponseEntity<ErrorEnvelope> handleApp(AppException ex) {
        return ResponseEntity.status(ex.status())
                .body(ErrorEnvelope.of(ex.code(), ex.getMessage(), ex.details()));
    }

    /**
     * Bean Validation failures on @Valid @RequestBody. Builds the same
     * {@code details.issues} array the Zod validator produced:
     * {@code [{ path: "body.<field>", message, code }]}.
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorEnvelope> handleValidation(MethodArgumentNotValidException ex) {
        List<Map<String, String>> issues = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> Map.of(
                        "path", "body." + fe.getField(),
                        "message", fe.getDefaultMessage() == null ? "" : fe.getDefaultMessage(),
                        "code", fe.getCode() == null ? "" : fe.getCode()
                ))
                .toList();
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ErrorEnvelope.of(ErrorCode.VALIDATION_FAILED, "Request validation failed",
                        Map.of("issues", issues)));
    }

    /** Malformed or missing JSON body — treated as a validation failure (400). */
    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ErrorEnvelope> handleUnreadable(HttpMessageNotReadableException ex) {
        Map<String, String> issue = Map.of(
                "path", "body",
                "message", "Malformed or missing JSON body",
                "code", "invalid_body"
        );
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(ErrorEnvelope.of(ErrorCode.VALIDATION_FAILED, "Request validation failed",
                        Map.of("issues", List.of(issue))));
    }

    /** Unknown route -> 404 in the standard envelope (instead of Spring's default page). */
    @ExceptionHandler(NoResourceFoundException.class)
    public ResponseEntity<ErrorEnvelope> handleNoResource(NoResourceFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ErrorEnvelope.of(ErrorCode.NOT_FOUND, "Resource not found", null));
    }

    /** Anything unexpected: log full detail server-side, return an opaque 500. */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ErrorEnvelope> handleUnknown(Exception ex, HttpServletRequest req) {
        log.error("[unhandled] {} {}", req.getMethod(), req.getRequestURI(), ex);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(ErrorEnvelope.of(ErrorCode.INTERNAL_ERROR, "Internal server error", null));
    }
}
