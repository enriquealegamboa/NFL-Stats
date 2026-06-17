package com.nflstats.backend.error;

/**
 * Machine-readable error codes returned in the error envelope.
 * Ported from the old {@code lib/errors.ts} {@code ErrorCode} object.
 */
public enum ErrorCode {
    VALIDATION_FAILED,
    NOT_FOUND,
    INTERNAL_ERROR
}
