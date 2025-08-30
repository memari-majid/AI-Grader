"""
Synthetic CS assignment and solution generator for CS AI Grader
"""

import random
from typing import Dict, List, Tuple, Any


# CS 1400 Assignment Templates based on course progression
CS_1400_ASSIGNMENTS = [
    {
        "name": "Hello World & Variables",
        "week": 1,
        "prompt": """Write a Python program that:
1. Asks the user for their name and age
2. Calculates what year they were born
3. Prints a personalized greeting with their birth year

Requirements:
- Use input() to get user data
- Use variables with meaningful names
- Include comments explaining your code
- Handle the calculation correctly""",
        "topics": ["variables", "input", "output", "basic_math"],
        "difficulty": "beginner"
    },
    {
        "name": "Calculator Functions",
        "week": 3,
        "prompt": """Create a calculator program with the following functions:
1. add(a, b) - returns sum
2. subtract(a, b) - returns difference  
3. multiply(a, b) - returns product
4. divide(a, b) - returns quotient (handle division by zero)

Requirements:
- Each function should have a docstring
- Include error handling for division by zero
- Test each function with sample inputs
- Use meaningful variable names""",
        "topics": ["functions", "parameters", "return_values", "error_handling"],
        "difficulty": "beginner"
    },
    {
        "name": "Grade Calculator",
        "week": 5,
        "prompt": """Write a program that calculates final grades:
1. Read student scores from user input (or use a list)
2. Calculate average score
3. Determine letter grade (A: 90+, B: 80-89, C: 70-79, D: 60-69, F: <60)
4. Print results with appropriate formatting

Requirements:
- Use conditional statements (if/elif/else)
- Handle edge cases (empty input, invalid scores)
- Include input validation
- Format output clearly""",
        "topics": ["conditionals", "lists", "loops", "validation"],
        "difficulty": "intermediate"
    },
    {
        "name": "File Processing",
        "week": 8,
        "prompt": """Create a program that processes a text file:
1. Read a text file line by line
2. Count total lines, words, and characters
3. Find the longest word
4. Write summary statistics to a new file

Requirements:
- Use file I/O operations (open, read, write)
- Handle file not found errors
- Process text efficiently
- Create well-formatted output file""",
        "topics": ["file_io", "string_processing", "error_handling", "loops"],
        "difficulty": "intermediate"
    },
    {
        "name": "Student Records System",
        "week": 12,
        "prompt": """Build a student records management system:
1. Create a Student class with name, ID, and grades
2. Implement methods to add grades and calculate GPA
3. Create a StudentRegistry class to manage multiple students
4. Include methods to find students and generate reports

Requirements:
- Use object-oriented programming principles
- Include proper encapsulation and data validation
- Implement __str__ methods for readable output
- Handle edge cases and invalid input""",
        "topics": ["classes", "objects", "encapsulation", "data_structures"],
        "difficulty": "advanced"
    }
]

# Common coding issues for realistic synthetic solutions
COMMON_ISSUES = [
    "missing_docstrings",
    "poor_variable_names", 
    "no_error_handling",
    "inefficient_algorithm",
    "style_violations",
    "missing_edge_cases",
    "hardcoded_values",
    "no_input_validation"
]

# Solution quality levels
QUALITY_LEVELS = {
    "excellent": {"score_range": (2.5, 3.0), "issues": 0},
    "good": {"score_range": (2.0, 2.5), "issues": 1},
    "fair": {"score_range": (1.5, 2.0), "issues": 2},
    "poor": {"score_range": (0.5, 1.5), "issues": 3}
}


def generate_synthetic_solution(assignment: Dict[str, Any], quality: str = "good") -> str:
    """Generate a synthetic solution based on assignment and quality level"""
    
    assignment_name = assignment["name"]
    topics = assignment["topics"]
    
    if "Hello World" in assignment_name:
        return _generate_hello_world_solution(quality)
    elif "Calculator" in assignment_name:
        return _generate_calculator_solution(quality)
    elif "Grade Calculator" in assignment_name:
        return _generate_grade_calculator_solution(quality)
    elif "File Processing" in assignment_name:
        return _generate_file_processing_solution(quality)
    elif "Student Records" in assignment_name:
        return _generate_student_records_solution(quality)
    else:
        return _generate_generic_solution(assignment, quality)


def _generate_hello_world_solution(quality: str) -> str:
    """Generate Hello World solution with varying quality"""
    
    if quality == "excellent":
        return '''"""
Hello World program with user input and age calculation.
Author: Student Name
Date: Today
"""

def main():
    """Main program function"""
    # Get user information
    name = input("What is your name? ")
    age_str = input("How old are you? ")
    
    try:
        age = int(age_str)
        birth_year = 2024 - age
        print(f"Hello {name}! You were born in {birth_year}.")
    except ValueError:
        print("Please enter a valid age as a number.")

if __name__ == "__main__":
    main()
'''
    elif quality == "good":
        return '''# Hello World program
def main():
    name = input("What is your name? ")
    age = int(input("How old are you? "))
    birth_year = 2024 - age
    print(f"Hello {name}! You were born in {birth_year}.")

main()
'''
    elif quality == "fair":
        return '''name = input("Name? ")
age = int(input("Age? "))
year = 2024 - age
print("Hello", name, "born in", year)
'''
    else:  # poor
        return '''n = input("name")
a = input("age")
y = 2024 - a
print(n, y)
'''


def _generate_calculator_solution(quality: str) -> str:
    """Generate calculator solution with varying quality"""
    
    if quality == "excellent":
        return '''"""
Calculator program with basic arithmetic operations.
Includes proper error handling and documentation.
"""

def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b

def subtract(a: float, b: float) -> float:
    """Return the difference of a and b."""
    return a - b

def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b

def divide(a: float, b: float) -> float:
    """Return the quotient of a and b.
    
    Raises:
        ValueError: If b is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def main():
    """Test the calculator functions"""
    # Test cases
    print("Testing calculator functions:")
    print(f"5 + 3 = {add(5, 3)}")
    print(f"10 - 4 = {subtract(10, 4)}")
    print(f"6 * 7 = {multiply(6, 7)}")
    
    try:
        print(f"15 / 3 = {divide(15, 3)}")
        print(f"10 / 0 = {divide(10, 0)}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
'''
    elif quality == "good":
        return '''def add(a, b):
    """Return sum of a and b"""
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        return "Error: Cannot divide by zero"
    return a / b

# Test the functions
print(add(5, 3))
print(subtract(10, 4))
print(multiply(6, 7))
print(divide(15, 3))
print(divide(10, 0))
'''
    else:  # fair or poor
        return '''def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mult(a, b):
    return a * b

def div(a, b):
    return a / b

print(add(5, 3))
print(div(10, 0))  # This will crash
'''


def _generate_grade_calculator_solution(quality: str) -> str:
    """Generate grade calculator solution"""
    
    if quality == "excellent":
        return '''"""
Grade calculator with input validation and proper formatting.
"""

def calculate_letter_grade(average: float) -> str:
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
    """Main program to calculate student grades."""
    scores = []
    
    print("Enter student scores (enter -1 to finish):")
    while True:
        try:
            score = float(input("Score: "))
            if score == -1:
                break
            if 0 <= score <= 100:
                scores.append(score)
            else:
                print("Please enter a score between 0 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    if scores:
        average = sum(scores) / len(scores)
        letter_grade = calculate_letter_grade(average)
        print(f"\\nAverage: {average:.2f}")
        print(f"Letter Grade: {letter_grade}")
    else:
        print("No valid scores entered")

if __name__ == "__main__":
    main()
'''
    else:  # good, fair, or poor
        return '''scores = [85, 92, 78, 88, 95]
average = sum(scores) / len(scores)

if average >= 90:
    grade = 'A'
elif average >= 80:
    grade = 'B'
elif average >= 70:
    grade = 'C'
else:
    grade = 'F'

print(f"Average: {average}")
print(f"Grade: {grade}")
'''


def _generate_file_processing_solution(quality: str) -> str:
    """Generate file processing solution"""
    return '''"""
File processing program to analyze text files.
"""

def analyze_text_file(filename: str) -> dict:
    """Analyze a text file and return statistics."""
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            
        total_lines = len(lines)
        total_words = 0
        total_chars = 0
        longest_word = ""
        
        for line in lines:
            words = line.split()
            total_words += len(words)
            total_chars += len(line)
            
            for word in words:
                if len(word) > len(longest_word):
                    longest_word = word
        
        return {
            'lines': total_lines,
            'words': total_words,
            'characters': total_chars,
            'longest_word': longest_word
        }
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        return None

def main():
    filename = input("Enter filename to analyze: ")
    stats = analyze_text_file(filename)
    
    if stats:
        print(f"File Statistics:")
        print(f"Lines: {stats['lines']}")
        print(f"Words: {stats['words']}")
        print(f"Characters: {stats['characters']}")
        print(f"Longest word: {stats['longest_word']}")

if __name__ == "__main__":
    main()
'''


def _generate_student_records_solution(quality: str) -> str:
    """Generate student records solution"""
    return '''"""
Student Records Management System
"""

class Student:
    """Represents a student with grades."""
    
    def __init__(self, name: str, student_id: str):
        """Initialize student with name and ID."""
        self.name = name
        self.student_id = student_id
        self.grades = []
    
    def add_grade(self, grade: float):
        """Add a grade to the student's record."""
        if 0 <= grade <= 100:
            self.grades.append(grade)
        else:
            raise ValueError("Grade must be between 0 and 100")
    
    def calculate_gpa(self) -> float:
        """Calculate and return the student's GPA."""
        if not self.grades:
            return 0.0
        return sum(self.grades) / len(self.grades)
    
    def __str__(self) -> str:
        """Return string representation of student."""
        gpa = self.calculate_gpa()
        return f"{self.name} (ID: {self.student_id}) - GPA: {gpa:.2f}"


class StudentRegistry:
    """Manages a collection of students."""
    
    def __init__(self):
        """Initialize empty registry."""
        self.students = {}
    
    def add_student(self, student: Student):
        """Add a student to the registry."""
        self.students[student.student_id] = student
    
    def find_student(self, student_id: str) -> Student:
        """Find and return student by ID."""
        return self.students.get(student_id)
    
    def generate_report(self) -> str:
        """Generate a report of all students."""
        if not self.students:
            return "No students in registry"
        
        report = "Student Registry Report\\n"
        report += "=" * 30 + "\\n"
        for student in self.students.values():
            report += str(student) + "\\n"
        return report


def main():
    """Test the student records system."""
    registry = StudentRegistry()
    
    # Create test students
    student1 = Student("Alice Johnson", "12345")
    student1.add_grade(85)
    student1.add_grade(92)
    student1.add_grade(78)
    
    student2 = Student("Bob Smith", "67890")
    student2.add_grade(95)
    student2.add_grade(88)
    
    registry.add_student(student1)
    registry.add_student(student2)
    
    print(registry.generate_report())

if __name__ == "__main__":
    main()
'''


def _generate_generic_solution(assignment: Dict[str, Any], quality: str) -> str:
    """Generate a generic solution for unknown assignment types"""
    return f'''# Solution for: {assignment["name"]}
# Topics: {", ".join(assignment.get("topics", []))}

def main():
    """Main program function"""
    print("This is a placeholder solution")
    # TODO: Implement according to assignment requirements
    pass

if __name__ == "__main__":
    main()
'''


def generate_cs_assignment_data(count: int = 5) -> List[Dict[str, Any]]:
    """Generate synthetic CS assignment data for testing"""
    assignments = []
    
    for i in range(count):
        # Pick a random assignment template
        template = random.choice(CS_1400_ASSIGNMENTS)
        
        # Generate solution with random quality
        quality = random.choice(["excellent", "good", "fair", "poor"])
        solution_code = generate_synthetic_solution(template, quality)
        
        # Create assignment data
        assignment_data = {
            'course': 'CS 1400',
            'assignment_name': f"{template['name']} - Student {i+1}",
            'assignment_prompt': template['prompt'],
            'student_code': solution_code,
            'topics': template['topics'],
            'difficulty': template['difficulty'],
            'week': template['week'],
            'expected_quality': quality,
            'synthetic': True
        }
        
        assignments.append(assignment_data)
    
    return assignments


def get_sample_assignment() -> Dict[str, Any]:
    """Get a single sample assignment for quick testing"""
    template = random.choice(CS_1400_ASSIGNMENTS[:3])  # Use easier assignments
    quality = random.choice(["good", "fair"])
    
    return {
        'course': 'CS 1400',
        'assignment_name': template['name'],
        'assignment_prompt': template['prompt'],
        'student_code': generate_synthetic_solution(template, quality),
        'topics': template['topics'],
        'difficulty': template['difficulty'],
        'synthetic': True
    }
