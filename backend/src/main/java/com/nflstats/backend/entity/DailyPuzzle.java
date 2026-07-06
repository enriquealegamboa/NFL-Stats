package com.nflstats.backend.entity;

import java.time.LocalDate;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "daily_puzzle")
public class DailyPuzzle {
    @Id
    @Column(name = "puzzle_date") private LocalDate puzzleDate;

    @Column(name = "team_id") private Integer teamId;

    @Column(name = "season_id") private Integer seasonId;

    @Column(name = "regular_season") private Boolean regularSeason;

    protected DailyPuzzle(){}

    public LocalDate getPuzzleDate(){return puzzleDate;}
    public Integer getTeamId(){return teamId;}
    public Integer getSeasonId(){return seasonId;}
    public Boolean getRegularSeason(){return regularSeason;}

}
