package com.nflstats.backend.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/** Root health check: GET / -> { "name": "nfl-stats-backend", "status": "ok" }. */
@RestController
public class RootController {

    @GetMapping("/")
    public Map<String, String> root() {
        return Map.of("name", "nfl-stats-backend", "status", "ok");
    }
}
