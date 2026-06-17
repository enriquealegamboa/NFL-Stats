package com.nflstats.backend;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Application entry point. Equivalent to the old Express {@code server.ts}:
 * Spring Boot starts an embedded web server and wires up the controllers,
 * the global error handler, and CORS automatically via component scanning.
 */
@SpringBootApplication
public class BackendApplication {
    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);
    }
}
