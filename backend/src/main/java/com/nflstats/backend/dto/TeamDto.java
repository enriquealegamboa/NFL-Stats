package com.nflstats.backend.dto;

import com.nflstats.backend.entity.Team;

public record TeamDto(
    Integer id,
    String name,
    String abbreviation,
    String conference,
    String division
) {
    public static TeamDto from(Team t){
        return new TeamDto(
            t.getTeamId(),
            t.getTeamName(),
            t.getAbbreviation(),
            t.getConference(),
            t.getDivision()
        );
    }
}