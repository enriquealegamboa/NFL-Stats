package com.nflstats.backend.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "team")
public class Team {

    @Id
    @Column(name = "team_id") private Integer teamId;

    @Column(name = "team_name") private String teamName;

    @Column(name = "abbreviation") private String abbreviation;

    @Column(name = "conference") private String conference;

    @Column(name = "division") private String division;

    protected Team(){}

    public Integer getTeamId() {return teamId;}
    public String getTeamName() {return teamName;}
    public String getAbbreviation() {return abbreviation;}
    public String getConference() {return conference;}
    public String getDivision() {return division;}
}
