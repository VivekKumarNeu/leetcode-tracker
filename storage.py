"""
Storage module for persisting user data.
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from models import ProblemProgress, Session, StudyPlan, Problem


class Storage:
    """Handles all data persistence."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.progress_file = self.data_dir / "progress.json"
        self.sessions_file = self.data_dir / "sessions.json"
        self.study_plan_file = self.data_dir / "study_plan.json"
        self.problems_file = self.data_dir / "neetcode150.json"
        
        self._init_files()
    
    def _init_files(self):
        """Initialize empty files if they don't exist."""
        if not self.progress_file.exists():
            self._save_json(self.progress_file, {})
        if not self.sessions_file.exists():
            self._save_json(self.sessions_file, [])
        if not self.study_plan_file.exists():
            self._save_json(self.study_plan_file, StudyPlan().to_dict())
    
    def _load_json(self, filepath: Path) -> dict:
        """Load JSON from file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _save_json(self, filepath: Path, data: dict or list):
        """Save JSON to file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_problems(self) -> List[Problem]:
        """Load all problems from the NeetCode 150 list."""
        data = self._load_json(self.problems_file)
        problems = []
        for category, problem_list in data.items():
            for p in problem_list:
                problem = Problem(
                    id=p["id"],
                    title=p["title"],
                    difficulty=p["difficulty"],
                    url=p["url"],
                    pattern=p["pattern"],
                    category=category
                )
                problems.append(problem)
        return sorted(problems, key=lambda x: x.id)
    
    def load_progress(self) -> Dict[int, ProblemProgress]:
        """Load all problem progress."""
        data = self._load_json(self.progress_file)
        return {
            int(k): ProblemProgress.from_dict(v) 
            for k, v in data.items()
        }
    
    def save_progress(self, progress: Dict[int, ProblemProgress]):
        """Save all problem progress."""
        data = {str(k): v.to_dict() for k, v in progress.items()}
        self._save_json(self.progress_file, data)
    
    def get_problem_progress(self, problem_id: int) -> ProblemProgress:
        """Get progress for a specific problem."""
        progress = self.load_progress()
        if problem_id not in progress:
            progress[problem_id] = ProblemProgress(problem_id=problem_id)
            self.save_progress(progress)
        return progress[problem_id]
    
    def update_problem_progress(self, problem_id: int, progress: ProblemProgress):
        """Update progress for a specific problem."""
        all_progress = self.load_progress()
        all_progress[problem_id] = progress
        self.save_progress(all_progress)
    
    def load_sessions(self) -> List[Session]:
        """Load all study sessions."""
        data = self._load_json(self.sessions_file)
        return [Session.from_dict(s) for s in data]
    
    def save_sessions(self, sessions: List[Session]):
        """Save all study sessions."""
        data = [s.to_dict() for s in sessions]
        self._save_json(self.sessions_file, data)
    
    def add_session(self, session: Session):
        """Add a new session."""
        sessions = self.load_sessions()
        sessions.append(session)
        self.save_sessions(sessions)
    
    def load_study_plan(self) -> StudyPlan:
        """Load study plan."""
        data = self._load_json(self.study_plan_file)
        return StudyPlan.from_dict(data)
    
    def save_study_plan(self, plan: StudyPlan):
        """Save study plan."""
        self._save_json(self.study_plan_file, plan.to_dict())
    
    def get_stats(self) -> dict:
        """Get overall statistics."""
        problems = self.load_problems()
        progress = self.load_progress()
        sessions = self.load_sessions()
        
        total_problems = len(problems)
        solved = sum(1 for p in progress.values() if p.status == "solved")
        attempted = len(progress)
        
        by_difficulty = {"Easy": 0, "Medium": 0, "Hard": 0}
        for problem in problems:
            if problem.id in progress and progress[problem.id].status == "solved":
                by_difficulty[problem.difficulty] += 1
        
        total_time = sum(s.total_time_minutes for s in sessions)
        
        return {
            "total_problems": total_problems,
            "solved": solved,
            "attempted": attempted,
            "unsolved": total_problems - attempted,
            "completion_percentage": round(solved / total_problems * 100, 2) if total_problems > 0 else 0,
            "by_difficulty": by_difficulty,
            "total_sessions": len(sessions),
            "total_time_hours": round(total_time / 60, 2)
        }
