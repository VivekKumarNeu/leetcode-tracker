"""
LLM Guide functionality for helping users solve problems.
"""
from typing import Dict, Optional
import json


class LeetCodeGuide:
    """Provides hints and guidance without giving away full solutions."""
    
    def __init__(self):
        # Hints database (in real implementation, this could be a separate JSON file)
        self.hints_db = self._load_hints()
    
    def _load_hints(self) -> Dict:
        """Load hints for common patterns."""
        return {
            "arrays_hashing": {
                "pattern": "Use hash maps/sets for O(1) lookups",
                "common_approaches": [
                    "Hash map for counting frequencies",
                    "Set for detecting duplicates",
                    "Two-pass: populate hash map, then query",
                    "Single-pass: check while building"
                ]
            },
            "two_pointers": {
                "pattern": "Use two pointers to traverse from both ends or at different speeds",
                "common_approaches": [
                    "Start from both ends, move towards center",
                    "Fast and slow pointers (Floyd's cycle detection)",
                    "Sort first, then use two pointers",
                    "Sliding window variation"
                ]
            },
            "stack": {
                "pattern": "Use stack for LIFO operations and tracking",
                "common_approaches": [
                    "Use stack to track opening brackets",
                    "Monotonic stack for next greater/smaller",
                    "Stack for expression evaluation",
                    "Two stacks for min/max tracking"
                ]
            },
            "binary_search": {
                "pattern": "Divide search space in half each iteration",
                "common_approaches": [
                    "Classic binary search on sorted array",
                    "Binary search on answer space",
                    "Find boundary (first/last occurrence)",
                    "Search in rotated sorted array"
                ]
            },
            "sliding_window": {
                "pattern": "Maintain a window that satisfies certain conditions",
                "common_approaches": [
                    "Fixed size window",
                    "Variable size window (expand/shrink)",
                    "Two pointers as window boundaries",
                    "Hash map to track window contents"
                ]
            },
            "linked_list": {
                "pattern": "Use pointers to manipulate node connections",
                "common_approaches": [
                    "Reverse: iteratively rewire pointers",
                    "Fast/slow pointer for middle/cycle",
                    "Dummy head for edge cases",
                    "Merge: compare and rewire"
                ]
            },
            "trees": {
                "pattern": "Use recursion or iterative traversal",
                "common_approaches": [
                    "DFS: Preorder, Inorder, Postorder",
                    "BFS: Level-order with queue",
                    "Divide and conquer on subtrees",
                    "Track path or parent pointers"
                ]
            },
            "heap_priority_queue": {
                "pattern": "Use heap for efficient access to min/max elements",
                "common_approaches": [
                    "Min/max heap for k elements",
                    "Two heaps for median",
                    "Heap for merge k sorted",
                    "Priority queue for scheduling"
                ]
            },
            "backtracking": {
                "pattern": "Explore all possibilities with pruning",
                "common_approaches": [
                    "Decision tree with recursion",
                    "Prune invalid paths early",
                    "Track state and undo (backtrack)",
                    "Use constraints to limit search"
                ]
            },
            "dynamic_programming_1d": {
                "pattern": "Build solution from subproblems",
                "common_approaches": [
                    "DP[i] represents state at i",
                    "Fibonacci-like recurrence",
                    "DP with space optimization",
                    "Track max/min ending at i"
                ]
            },
            "dynamic_programming_2d": {
                "pattern": "Build solution using 2D table",
                "common_approaches": [
                    "DP[i][j] for two sequences",
                    "DP[i][j] for grid positions",
                    "Space optimization using 1D array",
                    "Bottom-up vs memoization"
                ]
            },
            "graphs": {
                "pattern": "Traverse or search graph structure",
                "common_approaches": [
                    "BFS for shortest path",
                    "DFS for connectivity/components",
                    "Union-Find for connected components",
                    "Topological sort for dependencies"
                ]
            },
            "greedy": {
                "pattern": "Make locally optimal choices",
                "common_approaches": [
                    "Sort and process in order",
                    "Track local min/max",
                    "Greedy interval scheduling",
                    "Jump game strategy"
                ]
            },
            "intervals": {
                "pattern": "Sort and merge overlapping intervals",
                "common_approaches": [
                    "Sort by start time",
                    "Track end time and merge",
                    "Count overlapping with sweep line",
                    "Greedy interval selection"
                ]
            }
        }
    
    def get_hint(self, category: str, difficulty: str, question_number: int = 1) -> str:
        """Get a hint for a problem category."""
        if category not in self.hints_db:
            return "No specific hints available. Try breaking the problem down into smaller parts."
        
        hint_data = self.hints_db[category]
        hints = hint_data.get("common_approaches", [])
        
        if not hints:
            return f"Pattern: {hint_data.get('pattern', 'No hint available')}"
        
        # Return hint based on question number (for progressive hints)
        if question_number > len(hints):
            return "No more hints available for this pattern."
            
        idx = question_number - 1
        return f"Hint {question_number}: {hints[idx]}"
    
    def get_pattern_explanation(self, category: str) -> str:
        """Get explanation of the pattern for a category."""
        if category not in self.hints_db:
            return "Pattern information not available."
        
        return self.hints_db[category].get("pattern", "No pattern explanation available.")
    
    def suggest_next_steps(self, status: str, attempts: int, last_solved: bool) -> str:
        """Suggest what to do next based on current state."""
        if status == "unsolved":
            return """💡 Getting Started:
1. Read the problem carefully and identify the pattern
2. Think about edge cases
3. Start with a brute force solution
4. Then optimize"""
        
        elif status == "solving":
            if attempts == 0:
                return "First attempt: Try writing out the solution on paper first."
            elif last_solved:
                return "Good progress! Try optimizing your solution for time/space."
            else:
                return """Stuck? Try:
1. Look at a similar solved problem
2. Review the pattern for this category
3. Ask for a hint
4. Take a 5-minute break"""
        
        elif status == "solved":
            return """Next steps:
1. Can you solve it more optimally?
2. Practice explaining your solution
3. Mark for review in a few days
4. Try a variation of the problem"""
        
        return "Keep practicing!"
    
    def analyze_performance(self, time_taken: int, difficulty: str, solved: bool) -> str:
        """Analyze performance on an attempt."""
        if not solved:
            return "Keep trying! Focus on understanding the pattern before coding."
        
        expected_times = {"Easy": 15, "Medium": 30, "Hard": 45}
        expected = expected_times.get(difficulty, 30)
        
        if time_taken <= expected:
            return f"Excellent! You solved it in {time_taken} min (target: {expected} min)."
        elif time_taken <= expected * 1.5:
            return f"Good! {time_taken} min is reasonable for {difficulty}. Keep practicing!"
        else:
            return f"⏱Took {time_taken} min. Review the optimal solution to improve speed."
