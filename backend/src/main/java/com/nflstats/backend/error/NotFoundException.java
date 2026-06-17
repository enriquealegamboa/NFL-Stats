package com.nflstats.backend.error;

import org.springframework.http.HttpStatus;

/** 404 error, ported from the {@code NotFoundError} class in {@code lib/errors.ts}. */
public class NotFoundException extends AppException {

    public NotFoundException(String message) {
        this(message, null);
    }

    public NotFoundException(String message, Object details) {
        super(ErrorCode.NOT_FOUND, HttpStatus.NOT_FOUND.value(), message, details);
    }
}
