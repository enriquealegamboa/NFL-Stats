package com.nflstats.backend.repository;

import com.nflstats.backend.entity.DailyPuzzle;

import java.time.LocalDate;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;


public interface DailyPuzzleRepository extends JpaRepository<DailyPuzzle, LocalDate>{

    Optional<DailyPuzzle> findByPuzzleDate(LocalDate date);
}
