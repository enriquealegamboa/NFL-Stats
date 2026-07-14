package com.nflstats.backend.service;

import com.nflstats.backend.dto.DailyPuzzleResponse;
import com.nflstats.backend.entity.DailyPuzzle;
import com.nflstats.backend.error.NotFoundException;
import com.nflstats.backend.repository.DailyPuzzleRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.List;

@Service
public class DailyPuzzleService {
    private final DailyPuzzleRepository repo;
    private final int maxGuesses;
    private final String zone;
    private final List<String> statCategories;

    public DailyPuzzleService(
        DailyPuzzleRepository repo,
            @Value("${app.daily.max-guesses}") int maxGuesses,
            @Value("${app.daily.zone}") String zone,
            @Value("${app.daily.stat-categories}") List<String> statCategories
    ){
        this.repo = repo;
        this.maxGuesses = maxGuesses;
        this.zone = zone;
        this.statCategories = statCategories;
    }

    public DailyPuzzleResponse getToday(){
        LocalDate today = LocalDate.now(ZoneId.of(zone));
        return getForDate(today);
    }

    public DailyPuzzleResponse getForDate(LocalDate date){
        if (!repo.existsById(date)) {
            throw new NotFoundException("No puzzle found for " + date);
        }
        String id = date.toString();

        return new DailyPuzzleResponse(
                id,                           
                id,                                    
                maxGuesses,
                statCategories
        );
    }
}
