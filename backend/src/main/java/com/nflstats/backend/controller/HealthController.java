package com.nflstats.backend.controller;

import com.nflstats.backend.dto.EchoRequest;
import com.nflstats.backend.dto.EchoResponse;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.lang.management.ManagementFactory;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Health endpoints, ported from the old Express {@code routes/health.ts}.
 * <ul>
 *   <li>GET  /health       -&gt; { "status": "ok", "uptime": &lt;seconds&gt; }</li>
 *   <li>POST /health/echo  -&gt; { "echoed": "&lt;message&gt;" } (validation smoke test)</li>
 * </ul>
 */
@RestController
@RequestMapping("/health")
public class HealthController {

    @GetMapping
    public Map<String, Object> health() {
        // process.uptime() in Node returns seconds since start; the JVM exposes
        // uptime in milliseconds, so divide to match the original contract.
        double uptimeSeconds = ManagementFactory.getRuntimeMXBean().getUptime() / 1000.0;
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("status", "ok");
        body.put("uptime", uptimeSeconds);
        return body;
    }

    @PostMapping("/echo")
    public EchoResponse echo(@Valid @RequestBody EchoRequest request) {
        return new EchoResponse(request.message());
    }
}
