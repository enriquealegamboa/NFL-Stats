package com.nflstats.backend.controller;

import com.nflstats.backend.dto.TeamDto;
import com.nflstats.backend.dto.TeamsResponse;
import com.nflstats.backend.repository.TeamRepository;
import org.springframework.http.CacheControl;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Duration;
import java.util.List;

@RestController
@RequestMapping("/api/teams")
public class TeamController {
    private final TeamRepository teamRepository;

    public TeamController(TeamRepository teamRepository){
        this.teamRepository = teamRepository;
    }

    @GetMapping
    public ResponseEntity<TeamsResponse> getTeams(){
        List<TeamDto> teams = teamRepository.findAllByOrderByTeamNameAsc()
            .stream()
            .map(TeamDto::from)
            .toList();

        return ResponseEntity.ok()
                .cacheControl(CacheControl.maxAge(Duration.ofHours(1)).cachePublic())
                .body(new TeamsResponse(teams));
    }
}
