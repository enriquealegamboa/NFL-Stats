package com.nflstats.backend.error;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * The standard error response shape, identical to the old TypeScript envelope:
 * <pre>{ "error": { "code": "...", "message": "...", "details"?: ... } }</pre>
 * {@code details} is omitted from the JSON when null (via {@link JsonInclude}).
 */
public record ErrorEnvelope(Body error) {

    @JsonInclude(JsonInclude.Include.NON_NULL)
    public record Body(ErrorCode code, String message, Object details) {
    }

    public static ErrorEnvelope of(ErrorCode code, String message, Object details) {
        return new ErrorEnvelope(new Body(code, message, details));
    }
}
