package com.nflstats.backend.repository;

import com.nflstats.backend.entity.Team;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface TeamRepository extends JpaRepository<Team, Integer>{

    List<Team> findAllByOrderByTeamNameAsc();
}