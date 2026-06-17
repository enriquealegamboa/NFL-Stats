package com.nflstats.backend.dto;

/** Response for POST /health/echo: { "echoed": "<message>" }. */
public record EchoResponse(String echoed) {
}
