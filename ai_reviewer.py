import os
from github import Github
import google.generativeai as genai

# Initialize clients
github_token = os.getenv('GITHUB_TOKEN')
gemini_key = os.getenv('GEMINI_API_KEY')
pr_number = int(os.getenv('PR_NUMBER'))
repo_name = os.getenv('GITHUB_REPOSITORY')

g = Github(github_token)
repo = g.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# Configure Gemini
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_pr_diff():
    # Fetch the diff of the PR
    comparison = repo.get_compare(pr.base.sha, pr.head.sha)
    diff_text = ""
    for file in comparison.files:
        diff_text += f"File: {file.filename}\n{file.patch}\n\n"
    return diff_text

def get_ai_review(diff):
    prompt = (
        "You are a senior software engineer conducting a code review. "
        "Review the following code changes and provide constructive feedback, "
        "identifying bugs, security risks, or style issues. "
        "Keep your response concise and formatted in Markdown.\n\n"
        f"CODE DIFF:\n{diff}"
    )
    
    response = model.generate_content(prompt)
    return response.text

def main():
    print(f"Analyzing PR #{pr_number}...")
    diff = get_pr_diff()
    
    # Check if diff is too large for the prompt
    if len(diff) > 30000: 
        review = "⚠️ The PR diff is too large for a full AI review."
    else:
        review = get_ai_review(diff)
    
    # Post the comment to the PR
    pr.create_issue_comment(f"## 🤖 Gemini AI Code Review\n\n{review}")
    print("Review posted successfully.")

if __name__ == "__main__":
    main()
