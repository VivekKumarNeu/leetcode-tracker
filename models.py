"""
Data models for the LeetCode Tracker.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List
import json


@dataclass
class Problem:
    """Represents a LeetCode problem."""
    id: int
    title: str
    difficulty: str
    url: str
    pattern: str
    category: str = ""
    
    def __post_init__(self):
        """Set category based on problem ID ranges."""
        if not self.category:
            category_map = {
                (1, 9): "arrays_hashing",
                (10, 14): "two_pointers",
                (15, 20): "stack",
                (21, 27): "binary_search",
                (28, 33): "sliding_window",
                (34, 44): "linked_list",
                (45, 59): "trees",
                (60, 66): "heap_priority_queue",
                (67, 75): "backtracking",
                (76, 78): "tries",
                (79, 91): "graphs",
                (92, 97): "advanced_graphs",
                (98, 109): "dynamic_programming_1d",
                (110, 117): "dynamic_programming_2d",
                (118, 125): "greedy",
                (126, 131): "intervals",
                (132, 139): "math_geometry",
                (140, 145): "bit_manipulation"
            }
            for (start, end), cat in category_map.items():
                if start <= self.id <= end:
                    self.category = cat
                    break


@dataclass
class Attempt:
    """Represents an attempt at solving a problem."""
    timestamp: str
    solved: bool
    time_taken_minutes: int
    notes: str = ""
    solution_code: str = ""
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "solved": self.solved,
            "time_taken_minutes": self.time_taken_minutes,
            "notes": self.notes,
            "solution_code": self.solution_code
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Attempt":
        return cls(**data)


@dataclass
class ProblemProgress:
    """Tracks progress for a specific problem."""
    problem_id: int
    status: str = "unsolved"  # unsolved, solving, solved, reviewing
    attempts: List[Attempt] = field(default_factory=list)
    last_attempt_date: Optional[str] = None
    next_review_date: Optional[str] = None
    confidence_level: int = 0  # 0-5 scale
    
    def to_dict(self) -> dict:
        return {
            "problem_id": self.problem_id,
            "status": self.status,
            "attempts": [a.to_dict() for a in self.attempts],
            "last_attempt_date": self.last_attempt_date,
            "next_review_date": self.next_review_date,
            "confidence_level": self.confidence_level
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProblemProgress":
        attempts = [Attempt.from_dict(a) for a in data.get("attempts", [])]
        return cls(
            problem_id=data["problem_id"],
            status=data.get("status", "unsolved"),
            attempts=attempts,
            last_attempt_date=data.get("last_attempt_date"),
            next_review_date=data.get("next_review_date"),
            confidence_level=data.get("confidence_level", 0)
        )


@dataclass
class Session:
    """Represents a practice session."""
    session_id: str
    date: str
    problems_attempted: List[int] = field(default_factory=list)
    total_time_minutes: int = 0
    notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "date": self.date,
            "problems_attempted": self.problems_attempted,
            "total_time_minutes": self.total_time_minutes,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(**data)


@dataclass
class StudyPlan:
    """Represents a user's study plan."""
    daily_goal: int = 2
    preferred_difficulty: List[str] = field(default_factory=lambda: ["Easy", "Medium"])
    focus_categories: List[str] = field(default_factory=list)
    exclude_solved_days: int = 7  # Don't show solved problems for X days
    
    def to_dict(self) -> dict:
        return {
            "daily_goal": self.daily_goal,
            "preferred_difficulty": self.preferred_difficulty,
            "focus_categories": self.focus_categories,
            "exclude_solved_days": self.exclude_solved_days
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StudyPlan":
        return cls(**data)
