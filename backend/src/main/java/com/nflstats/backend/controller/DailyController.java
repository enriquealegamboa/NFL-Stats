package com.nflstats.backend.controller;


import com.nflstats.backend.dto.DailyPuzzleResponse;
import com.nflstats.backend.service.DailyPuzzleService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("api/daily")
public class DailyController {
    private final DailyPuzzleService service;

    public DailyController(DailyPuzzleService service){
        this.service = service;
    }

    @GetMapping("/today")
    public ResponseEntity<DailyPuzzleResponse> today(){
        return ResponseEntity.ok(service.getToday());
    }
}
