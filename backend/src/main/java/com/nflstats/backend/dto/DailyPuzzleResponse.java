package com.nflstats.backend.dto;

import java.util.List;

public record DailyPuzzleResponse(
    String puzzleId,
    String date,
    int maxGuesses,
    List<String> statCategories
){}
