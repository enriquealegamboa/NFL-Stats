package com.nflstats.backend;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * Locks the HTTP contract the frontend depends on: the three endpoints and the
 * standardized validation error envelope.
 */
@SpringBootTest
@AutoConfigureMockMvc
class HealthContractTest {

    @Autowired
    MockMvc mvc;

    @Test
    void rootReturnsNameAndStatus() throws Exception {
        mvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.name").value("nfl-stats-backend"))
                .andExpect(jsonPath("$.status").value("ok"));
    }

    @Test
    void healthReturnsStatusAndUptime() throws Exception {
        mvc.perform(get("/health"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("ok"))
                .andExpect(jsonPath("$.uptime").isNumber());
    }

    @Test
    void echoReturnsTheMessage() throws Exception {
        mvc.perform(post("/health/echo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"message\":\"hi\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.echoed").value("hi"));
    }

    @Test
    void echoRejectsEmptyMessageWithValidationEnvelope() throws Exception {
        mvc.perform(post("/health/echo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"message\":\"\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_FAILED"))
                .andExpect(jsonPath("$.error.message").value("Request validation failed"))
                .andExpect(jsonPath("$.error.details.issues").isArray())
                .andExpect(jsonPath("$.error.details.issues[0].path").value("body.message"));
    }

    @Test
    void echoRejectsMissingBodyWithValidationEnvelope() throws Exception {
        mvc.perform(post("/health/echo")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(""))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.error.code").value("VALIDATION_FAILED"));
    }
}
