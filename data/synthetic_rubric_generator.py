"""
Synthetic rubric generator for CS assignments
Creates rubrics tailored to specific programming assignments
"""

from typing import Dict, List, Any
import random


def generate_rubric_for_assignment(assignment_type: str, topics: List[str]) -> Dict[str, Any]:
    """Generate a rubric tailored to a specific CS assignment"""
    
    base_criteria = get_base_cs_criteria()
    topic_specific_criteria = get_topic_specific_criteria(topics)
    
    # Combine base + topic-specific criteria
    all_criteria = base_criteria + topic_specific_criteria
    
    # Create rubric
    rubric = {
        "name": f"{assignment_type} - Auto-Generated Rubric",
        "version": "1.0",
        "assignment_type": assignment_type,
        "topics": topics,
        "scale": {
            "min": 0,
            "max": 3,
            "labels": {
                "0": "Does not meet expectations",
                "1": "Approaching expectations", 
                "2": "Meets expectations",
                "3": "Exceeds expectations"
            }
        },
        "criteria": all_criteria
    }
    
    return rubric


def get_base_cs_criteria() -> List[Dict[str, Any]]:
    """Base criteria that apply to most CS assignments"""
    return [
        {
            "id": "CORR",
            "code": "CORR",
            "title": "Correctness",
            "category": "Functionality",
            "description": "Program produces correct outputs for given inputs",
            "levels": {
                "0": "Program fails to run or produces incorrect results for most test cases",
                "1": "Program runs but produces incorrect results for some test cases",
                "2": "Program produces correct results for most test cases",
                "3": "Program produces correct results for all test cases including edge cases"
            }
        },
        {
            "id": "STYLE",
            "code": "STYLE", 
            "title": "Code Style and Readability",
            "category": "Code Quality",
            "description": "Code follows Python conventions and is easy to read",
            "levels": {
                "0": "Code is very difficult to read with inconsistent or poor style",
                "1": "Code has some style issues that impact readability",
                "2": "Code generally follows good style conventions and is readable",
                "3": "Code exemplifies excellent style with clear, consistent formatting"
            }
        },
        {
            "id": "DOC",
            "code": "DOC",
            "title": "Documentation",
            "category": "Communication",
            "description": "Code includes appropriate comments and docstrings",
            "levels": {
                "0": "No meaningful documentation or comments",
                "1": "Minimal documentation; some functions lack docstrings",
                "2": "Adequate documentation with most functions documented",
                "3": "Comprehensive documentation with clear, helpful docstrings and comments"
            }
        }
    ]


def get_topic_specific_criteria(topics: List[str]) -> List[Dict[str, Any]]:
    """Generate criteria specific to the assignment topics"""
    criteria = []
    
    if "functions" in topics:
        criteria.append({
            "id": "FUNC",
            "code": "FUNC",
            "title": "Function Design",
            "category": "Program Structure",
            "description": "Functions are well-designed with appropriate parameters and return values",
            "levels": {
                "0": "Functions are poorly designed or missing",
                "1": "Functions exist but have design issues (parameters, return values)",
                "2": "Functions are well-designed and serve their purpose effectively",
                "3": "Functions demonstrate excellent design principles and reusability"
            }
        })
    
    if "error_handling" in topics:
        criteria.append({
            "id": "ERR",
            "code": "ERR",
            "title": "Error Handling",
            "category": "Robustness",
            "description": "Program handles errors and edge cases appropriately",
            "levels": {
                "0": "No error handling; program crashes on invalid input",
                "1": "Minimal error handling; some edge cases not addressed",
                "2": "Good error handling for most common error conditions",
                "3": "Comprehensive error handling with informative error messages"
            }
        })
    
    if "loops" in topics:
        criteria.append({
            "id": "LOOP",
            "code": "LOOP",
            "title": "Loop Implementation",
            "category": "Control Structures",
            "description": "Loops are used correctly and efficiently",
            "levels": {
                "0": "Loops are incorrect or missing where needed",
                "1": "Loops work but are inefficient or poorly structured",
                "2": "Loops are correctly implemented and reasonably efficient",
                "3": "Loops demonstrate excellent understanding and optimal implementation"
            }
        })
    
    if "conditionals" in topics:
        criteria.append({
            "id": "COND",
            "code": "COND", 
            "title": "Conditional Logic",
            "category": "Control Structures",
            "description": "Conditional statements are used correctly and handle all cases",
            "levels": {
                "0": "Conditional logic is incorrect or missing",
                "1": "Conditionals work for some cases but miss important scenarios",
                "2": "Conditional logic correctly handles most required cases",
                "3": "Conditional logic is comprehensive and handles all edge cases elegantly"
            }
        })
    
    if "file_io" in topics:
        criteria.append({
            "id": "FILE",
            "code": "FILE",
            "title": "File Operations",
            "category": "I/O Operations",
            "description": "File reading/writing operations are implemented correctly",
            "levels": {
                "0": "File operations fail or are not implemented",
                "1": "File operations work but lack proper error handling",
                "2": "File operations work correctly with basic error handling",
                "3": "File operations are robust with comprehensive error handling"
            }
        })
    
    if "classes" in topics or "objects" in topics:
        criteria.append({
            "id": "OOP",
            "code": "OOP",
            "title": "Object-Oriented Design",
            "category": "Design Principles",
            "description": "Classes and objects are designed and used appropriately",
            "levels": {
                "0": "Poor or missing object-oriented design",
                "1": "Basic OOP concepts used but with design issues",
                "2": "Good use of OOP principles with proper encapsulation",
                "3": "Excellent OOP design demonstrating advanced principles"
            }
        })
    
    if "validation" in topics:
        criteria.append({
            "id": "VAL",
            "code": "VAL",
            "title": "Input Validation",
            "category": "Data Handling",
            "description": "User input is properly validated and sanitized",
            "levels": {
                "0": "No input validation; accepts any input",
                "1": "Basic validation but misses some important cases",
                "2": "Good input validation for most expected scenarios",
                "3": "Comprehensive input validation with helpful user feedback"
            }
        })
    
    return criteria


def generate_assignment_package(difficulty: str = "intermediate") -> Dict[str, Any]:
    """Generate a complete assignment package: problem + rubric + sample solution"""
    
    # Assignment templates by difficulty
    templates = {
        "beginner": [
            {
                "name": "Hello World Plus",
                "topics": ["variables", "input", "output", "basic_math"],
                "prompt": """Write a Python program that:
1. Asks the user for their name and favorite number
2. Calculates the square of their favorite number
3. Prints a personalized message with the result

Requirements:
- Use meaningful variable names
- Include at least one comment
- Handle the calculation correctly""",
                "sample_solution": '''# Hello World Plus program
name = input("What is your name? ")
fav_num = int(input("What is your favorite number? "))

# Calculate the square
square = fav_num * fav_num

print(f"Hello {name}! The square of {fav_num} is {square}.")
'''
            }
        ],
        "intermediate": [
            {
                "name": "Grade Calculator Pro",
                "topics": ["functions", "conditionals", "loops", "validation"],
                "prompt": """Create a grade calculator program with these functions:

1. get_grades() - Get list of grades from user input
2. calculate_average(grades) - Calculate and return average
3. get_letter_grade(average) - Convert average to letter grade
4. main() - Coordinate the program flow

Grading scale: A(90+), B(80-89), C(70-79), D(60-69), F(<60)

Requirements:
- Include docstrings for all functions
- Validate input (grades 0-100)
- Handle empty grade lists
- Use appropriate error handling""",
                "sample_solution": '''def get_grades():
    """Get a list of grades from user input."""
    grades = []
    print("Enter grades (enter -1 to finish):")
    
    while True:
        try:
            grade = float(input("Grade: "))
            if grade == -1:
                break
            if 0 <= grade <= 100:
                grades.append(grade)
            else:
                print("Please enter a grade between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    return grades

def calculate_average(grades):
    """Calculate the average of a list of grades."""
    if not grades:
        return 0
    return sum(grades) / len(grades)

def get_letter_grade(average):
    """Convert numeric average to letter grade."""
    if average >= 90:
        return 'A'
    elif average >= 80:
        return 'B'
    elif average >= 70:
        return 'C'
    elif average >= 60:
        return 'D'
    else:
        return 'F'

def main():
    """Main program function."""
    grades = get_grades()
    
    if grades:
        avg = calculate_average(grades)
        letter = get_letter_grade(avg)
        print(f"Average: {avg:.2f}")
        print(f"Letter Grade: {letter}")
    else:
        print("No grades entered")

if __name__ == "__main__":
    main()
'''
            }
        ],
        "advanced": [
            {
                "name": "Student Database System",
                "topics": ["classes", "objects", "file_io", "error_handling", "data_structures"],
                "prompt": """Build a student database system with these requirements:

1. Student class with name, ID, and grades list
2. Database class to manage multiple students
3. Methods to add students, add grades, calculate GPAs
4. Save/load functionality to/from file
5. Search functionality by student ID or name

Requirements:
- Use proper OOP principles
- Include comprehensive error handling
- Implement file I/O for persistence
- Include input validation
- Write thorough documentation""",
                "sample_solution": '''import json

class Student:
    """Represents a student with grades."""
    
    def __init__(self, name, student_id):
        """Initialize student with name and ID."""
        self.name = name
        self.student_id = student_id
        self.grades = []
    
    def add_grade(self, grade):
        """Add a grade (0-100) to student record."""
        if not 0 <= grade <= 100:
            raise ValueError("Grade must be between 0 and 100")
        self.grades.append(grade)
    
    def calculate_gpa(self):
        """Calculate GPA on 4.0 scale."""
        if not self.grades:
            return 0.0
        avg = sum(self.grades) / len(self.grades)
        return min(4.0, avg / 25)  # Rough conversion
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'student_id': self.student_id,
            'grades': self.grades
        }

class StudentDatabase:
    """Manages a collection of students."""
    
    def __init__(self):
        """Initialize empty database."""
        self.students = {}
    
    def add_student(self, student):
        """Add student to database."""
        self.students[student.student_id] = student
    
    def find_by_id(self, student_id):
        """Find student by ID."""
        return self.students.get(student_id)
    
    def save_to_file(self, filename):
        """Save database to JSON file."""
        try:
            data = {sid: s.to_dict() for sid, s in self.students.items()}
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise IOError(f"Could not save to {filename}: {e}")
    
    def load_from_file(self, filename):
        """Load database from JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            for sid, sdata in data.items():
                student = Student(sdata['name'], sdata['student_id'])
                student.grades = sdata['grades']
                self.students[sid] = student
        except (IOError, json.JSONDecodeError) as e:
            raise IOError(f"Could not load from {filename}: {e}")
'''
            }
        ]
    }
    
    # Select template based on difficulty
    template_list = templates.get(difficulty, templates["intermediate"])
    template = random.choice(template_list)
    
    # Generate rubric for this assignment
    rubric = generate_rubric_for_assignment(template["name"], template["topics"])
    
    return {
        "assignment": {
            "name": template["name"],
            "prompt": template["prompt"],
            "topics": template["topics"],
            "difficulty": difficulty
        },
        "rubric": rubric,
        "sample_solution": template["sample_solution"],
        "package_id": f"{template['name'].lower().replace(' ', '_')}_{difficulty}"
    }


def generate_multiple_assignment_packages(count: int = 5) -> List[Dict[str, Any]]:
    """Generate multiple complete assignment packages"""
    packages = []
    difficulties = ["beginner", "intermediate", "advanced"]
    
    for i in range(count):
        difficulty = random.choice(difficulties)
        package = generate_assignment_package(difficulty)
        package["package_number"] = i + 1
        packages.append(package)
    
    return packages


def create_synthetic_grading_session(package: Dict[str, Any]) -> Dict[str, Any]:
    """Create a complete synthetic grading session from an assignment package"""
    
    assignment = package["assignment"]
    rubric = package["rubric"]
    solution = package["sample_solution"]
    
    # Simulate AI grading of the solution
    from services.code_analysis_service import analyze_python_code
    
    try:
        metrics = analyze_python_code(solution)
    except:
        metrics = {"lines": 0, "functions": 0, "classes": 0}
    
    # Generate synthetic scores based on solution quality
    scores = {}
    feedback = {}
    
    for criterion in rubric["criteria"]:
        crit_id = criterion["id"]
        
        # Base score on code quality indicators
        if crit_id == "CORR":
            # Correctness based on whether code looks complete
            score = 3 if "def " in solution and "return" in solution else 2
        elif crit_id == "STYLE":
            # Style based on line length and naming
            avg_line_len = len(solution) / max(metrics.get("lines", 1), 1)
            score = 3 if avg_line_len < 80 and "_" in solution else 2
        elif crit_id == "DOC":
            # Documentation based on docstring coverage
            doc_coverage = metrics.get("docstring_coverage", 0)
            if doc_coverage > 0.8:
                score = 3
            elif doc_coverage > 0.5:
                score = 2
            else:
                score = 1
        else:
            # Default scoring for topic-specific criteria
            score = random.choice([2, 3])  # Most synthetic solutions are decent
        
        scores[crit_id] = score
        
        # Generate feedback based on score
        level_desc = criterion["levels"][str(score)]
        feedback[crit_id] = f"[SYNTHETIC] {level_desc} The code demonstrates {criterion['title'].lower()} at this level."
    
    return {
        "assignment_package": package,
        "code_metrics": metrics,
        "ai_scores": scores,
        "ai_feedback": feedback,
        "grading_session": {
            "total_score": sum(scores.values()),
            "criteria_count": len(scores),
            "pass_rate": sum(1 for s in scores.values() if s >= 2) / len(scores)
        }
    }
