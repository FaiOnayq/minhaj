"""
Course Generation System
"""
from workflow import generate_course
import json


def main():
    print("=" * 80)
    print("COURSE GENERATION SYSTEM")
    print("=" * 80)
    
    # Input course specification
    course_input = {
        "course_title": "Introduction to Machine Learning",
        "subject_domain": "Artificial Intelligence",
        "duration_weeks": 8,
        "education_level": "Undergraduate",
        "teaching_goals": "Students should understand basic ML concepts and be able to build simple models using Python. Focus on practical labs and minimal math.",
        "reference_link": "https://scikit-learn.org/stable/"
    }
    
    print("\nInput:")
    print(json.dumps(course_input, indent=2))
    print("\n" + "=" * 80)
    print("GENERATING COURSE...\n")
    
    # Generate course
    course = generate_course(course_input)
    
    # Display result
    print("\n" + "=" * 80)
    print("GENERATED COURSE:")
    print("=" * 80)
    print(json.dumps(course, indent=2))
    
    # Save to file
    with open("generated_course.json", "w") as f:
        json.dump(course, f, indent=2)
    
    print("\n" + "=" * 80)
    print("✓ Course saved to: generated_course.json")


if __name__ == "__main__":
    main()