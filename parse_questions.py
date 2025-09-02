"""
HTML Parser for Student Questions
Extracts student names and questions from HTML files in a directory.
"""

import os
import glob
from bs4 import BeautifulSoup
import re
import argparse

def parse_html_file(file_path):
    """
    Parse a single HTML file to extract student name and questions.
    
    Args:
        file_path (str): Path to the HTML file
        
    Returns:
        dict: Dictionary containing student_name and questions list
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract student name from title or h1
        student_name = "Unknown Student"
        
        # Try to get from title first
        title = soup.find('title')
        if title:
            title_text = title.get_text().strip()
            # Look for pattern like "Questions 09/02: STUDENT NAME"
            match = re.search(r'Questions\s+\d+/\d+:\s*(.+)', title_text)
            if match:
                student_name = match.group(1).strip()
        
        # If not found in title, try h1
        if student_name == "Unknown Student":
            h1 = soup.find('h1')
            if h1:
                h1_text = h1.get_text().strip()
                match = re.search(r'Questions\s+\d+/\d+:\s*(.+)', h1_text)
                if match:
                    student_name = match.group(1).strip()
        
        # Extract questions from paragraph tags
        questions = []
        
        # Find the main content div
        content_div = soup.find('div')
        if content_div:
            paragraphs = content_div.find_all('p')
            
            current_question = ""
            for p in paragraphs:
                text = p.get_text().strip()
                
                # Skip empty paragraphs (like &nbsp;)
                if not text or text == '\xa0':
                    # If we have accumulated text, save it as a question
                    if current_question.strip():
                        questions.append(current_question.strip())
                        current_question = ""
                    continue
                
                # Accumulate text for current question
                if current_question:
                    current_question += " " + text
                else:
                    current_question = text
            
            # Don't forget the last question if file doesn't end with empty paragraph
            if current_question.strip():
                questions.append(current_question.strip())
        
        return {
            'student_name': student_name,
            'questions': questions,
            'file_path': file_path
        }
        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return {
            'student_name': "Error parsing file",
            'questions': [],
            'file_path': file_path
        }

def process_directory(directory_path):
    """
    Process all HTML files in a directory.
    
    Args:
        directory_path (str): Path to directory containing HTML files
        
    Returns:
        list: List of parsed student data
    """
    # Find all HTML files in directory
    html_files = glob.glob(os.path.join(directory_path, "*.html")) + \
                 glob.glob(os.path.join(directory_path, "*.htm"))
    
    if not html_files:
        print(f"No HTML files found in {directory_path}")
        return []
    
    print(f"Found {len(html_files)} HTML files to process...")
    
    results = []
    for file_path in sorted(html_files):
        print(f"Processing: {os.path.basename(file_path)}")
        result = parse_html_file(file_path)
        results.append(result)
    
    return results

def format_output(results):
    """
    Format the parsed results as a bulleted list.
    
    Args:
        results (list): List of parsed student data
        
    Returns:
        str: Formatted output string
    """
    output = []
    
    for result in results:
        output.append(f"- {result['student_name']}")
        
        for i, question in enumerate(result['questions'], 1):
            # Clean up question text - remove extra whitespace
            clean_question = ' '.join(question.split())
            output.append(f"    - Question {i}: {clean_question}")
        
        output.append("")  # Empty line between students
    
    return "\n".join(output)

def main():
    """
    Main function to run the HTML parser.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Parse HTML files to extract student names and questions'
    )
    parser.add_argument(
        'directory',
        help='Directory path containing HTML files to parse'
    )
    parser.add_argument(
        'output_file',
        help='Output file path to write parsed results'
    )
    
    args = parser.parse_args()
    
    # Validate directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory not found: {args.directory}")
        return 1
    
    if not os.path.isdir(args.directory):
        print(f"Error: Path is not a directory: {args.directory}")
        return 1
    
    # Process files
    results = process_directory(args.directory)
    
    if not results:
        print("No files processed.")
        return 1
    
    # Format output
    formatted_output = format_output(results)
    
    # Write to output file
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(os.path.abspath(args.output_file))
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(formatted_output)
        
        print(f"Successfully processed {len(results)} files")
        print(f"Results written to: {args.output_file}")
        return 0
        
    except Exception as e:
        print(f"Error writing to output file: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
