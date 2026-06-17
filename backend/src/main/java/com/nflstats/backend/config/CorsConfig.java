package com.nflstats.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.util.Arrays;

/**
 * CORS configuration, ported from the {@code cors(...)} middleware in the old
 * {@code server.ts}. Reads a comma-separated CORS_ORIGIN list (default "*").
 */
@Configuration
public class CorsConfig implements WebMvcConfigurer {

    private final String corsOrigin;

    public CorsConfig(@Value("${CORS_ORIGIN:*}") String corsOrigin) {
        this.corsOrigin = corsOrigin;
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        String[] origins = Arrays.stream(corsOrigin.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toArray(String[]::new);
        if (origins.length == 0) {
            origins = new String[]{"*"};
        }
        registry.addMapping("/**")
                .allowedOrigins(origins)
                .allowedMethods("*")
                .allowedHeaders("*");
    }
}
