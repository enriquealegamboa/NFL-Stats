package com.nflstats.backend.error;

/**
 * Base class for expected, client-facing errors. Carries the error code, the
 * HTTP status, and optional structured details — the Java equivalent of the
 * {@code AppError} class from the old {@code lib/errors.ts}.
 */
public class AppException extends RuntimeException {

    private final ErrorCode code;
    private final int status;
    private final transient Object details;

    public AppException(ErrorCode code, int status, String message, Object details) {
        super(message);
        this.code = code;
        this.status = status;
        this.details = details;
    }

    public ErrorCode code() {
        return code;
    }

    public int status() {
        return status;
    }

    public Object details() {
        return details;
    }
}
