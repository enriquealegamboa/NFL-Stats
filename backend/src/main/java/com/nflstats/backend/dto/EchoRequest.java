package com.nflstats.backend.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

/**
 * Body for POST /health/echo. Mirrors the Zod schema
 * {@code z.object({ message: z.string().min(1).max(280) })}:
 * the field is required (@NotNull) and its length must be 1..280 (@Size).
 */
public record EchoRequest(
        @NotNull @Size(min = 1, max = 280) String message
) {
}
