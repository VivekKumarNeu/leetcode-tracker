"""
Smart question selection algorithm.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from collections import defaultdict

from models import Problem, ProblemProgress, StudyPlan
from storage import Storage


class QuestionSelector:
    """Selects questions based on spaced repetition and user preferences."""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_daily_questions(self, count: int = 2, topic: Optional[str] = None) -> List[Dict]:
        """
        Get a set of questions for daily practice.
        Uses spaced repetition algorithm.
        """
        plan = self.storage.load_study_plan()
        problems = self.storage.load_problems()
        progress = self.storage.load_progress()
        
        # Build candidate list
        candidates = []
        
        for problem in problems:
            prog = progress.get(problem.id, ProblemProgress(problem_id=problem.id))
            
            # Skip if difficulty not preferred
            if problem.difficulty not in plan.preferred_difficulty:
                continue
            
            # If topic is specified, restrict to that topic key.
            # Otherwise, use user's focus categories filter (if any).
            if topic:
                if problem.category != topic:
                    continue
            else:
                if plan.focus_categories and problem.category not in plan.focus_categories:
                    continue
            
            score = self._calculate_priority(problem, prog, plan)
            if score > 0:
                candidates.append({
                    "problem": problem,
                    "progress": prog,
                    "score": score
                })
        
        # Sort by priority score (descending)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        # Select top N with some randomness for variety
        selected = []
        selected_ids = set()
        
        # First pass: take highest priority
        for c in candidates[:count]:
            selected.append(self._format_question(c["problem"], c["progress"]))
            selected_ids.add(c["problem"].id)
        
        # If not enough, fill with random unsolved
        if len(selected) < count:
            unsolved = [c for c in candidates if c["problem"].id not in selected_ids]
            random.shuffle(unsolved)
            for c in unsolved[:count - len(selected)]:
                selected.append(self._format_question(c["problem"], c["progress"]))
        
        return selected
    
    def _calculate_priority(self, problem: Problem, progress: ProblemProgress, plan: StudyPlan) -> float:
        """
        Calculate priority score for a problem.
        Higher score = should solve sooner.
        """
        score = 0.0
        
        # Never attempted gets high priority
        if progress.status == "unsolved":
            score += 100
        
        # Recently solved - check if due for review
        elif progress.status == "solved":
            if not progress.next_review_date:
                return 0  # Don't show until review is scheduled
            
            next_review = datetime.fromisoformat(progress.next_review_date)
            if datetime.now() >= next_review:
                # Overdue for review
                days_overdue = (datetime.now() - next_review).days
                score += 50 + (days_overdue * 10)
            else:
                return 0  # Not due yet
        
        # Currently solving - continue
        elif progress.status == "solving":
            score += 75
        
        # Boost based on difficulty preference (Easy = higher priority for beginners)
        difficulty_boost = {"Easy": 10, "Medium": 5, "Hard": 0}
        score += difficulty_boost.get(problem.difficulty, 0)
        
        # Boost focus categories
        if plan.focus_categories and problem.category in plan.focus_categories:
            score += 15
        
        # Penalize recent attempts
        if progress.last_attempt_date:
            last_attempt = datetime.fromisoformat(progress.last_attempt_date)
            days_since = (datetime.now() - last_attempt).days
            if days_since < 1:
                score *= 0.3  # Very recent
            elif days_since < 3:
                score *= 0.6  # Somewhat recent
        
        return score
    
    def _format_question(self, problem: Problem, progress: ProblemProgress) -> Dict:
        """Format a question for display."""
        attempts = len(progress.attempts)
        
        # Get last attempt info
        last_time = None
        last_solved = False
        if progress.attempts:
            last_attempt = progress.attempts[-1]
            last_time = last_attempt.time_taken_minutes
            last_solved = last_attempt.solved
        
        return {
            "id": problem.id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "category": problem.category,
            "pattern": problem.pattern,
            "url": problem.url,
            "status": progress.status,
            "attempts": attempts,
            "last_time_minutes": last_time,
            "last_solved": last_solved,
            "confidence": progress.confidence_level
        }
    
    def get_review_questions(self, count: int = 3) -> List[Dict]:
        """Get questions due for review based on spaced repetition."""
        plan = self.storage.load_study_plan()
        progress = self.storage.load_progress()
        problems = {p.id: p for p in self.storage.load_problems()}
        
        review_candidates = []
        
        for prog in progress.values():
            if prog.status == "solved" and prog.next_review_date:
                next_review = datetime.fromisoformat(prog.next_review_date)
                if datetime.now() >= next_review:
                    problem = problems.get(prog.problem_id)
                    if problem:
                        review_candidates.append({
                            "problem": problem,
                            "progress": prog
                        })
        
        # Sort by review date (oldest first)
        review_candidates.sort(key=lambda x: x["progress"].next_review_date)
        
        return [
            self._format_question(c["problem"], c["progress"])
            for c in review_candidates[:count]
        ]
    
    def get_progress_by_category(self) -> Dict:
        """Get completion stats grouped by category."""
        problems = self.storage.load_problems()
        progress = self.storage.load_progress()
        
        stats = defaultdict(lambda: {"total": 0, "solved": 0, "attempted": 0})
        
        for problem in problems:
            cat = problem.category
            stats[cat]["total"] += 1
            
            if problem.id in progress:
                stats[cat]["attempted"] += 1
                if progress[problem.id].status == "solved":
                    stats[cat]["solved"] += 1
        
        return dict(stats)
    
    def search_questions(self, query: str = "", category: str = "", difficulty: str = "", 
                        status: str = "") -> List[Dict]:
        """Search and filter questions."""
        problems = self.storage.load_problems()
        progress = self.storage.load_progress()
        
        results = []
        for problem in problems:
            prog = progress.get(problem.id, ProblemProgress(problem_id=problem.id))
            
            # Apply filters
            if query and query.lower() not in problem.title.lower():
                continue
            if category and problem.category != category:
                continue
            if difficulty and problem.difficulty != difficulty:
                continue
            if status and prog.status != status:
                continue
            
            results.append(self._format_question(problem, prog))
        
        return results
