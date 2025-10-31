"""Prompts for analyzing user test feedback"""

ANALYZE_FEEDBACK_PROMPT = """You are an expert UX researcher analyzing user feedback from prototype testing.

Project: {project_name}
Project Goal: {project_goal}
Prototype Page Tested: {page_name}

Test Feedback Collected:
{feedback_data}

Please provide a comprehensive analysis with the following sections:

## 1. Overall Sentiment
Analyze the overall sentiment (positive, negative, neutral) and provide a sentiment score (e.g., 70% positive, 20% neutral, 10% negative).

## 2. Key Themes
Identify 3-5 recurring themes or topics from the feedback. Group similar comments together.

## 3. Pain Points & Issues
List specific usability issues, confusions, or problems users encountered. Categorize each by severity:
- 🔴 CRITICAL: Blocks core functionality or causes major confusion
- 🟠 HIGH: Significant usability issue affecting user experience
- 🟡 MEDIUM: Minor inconvenience but doesn't block usage
- 🟢 LOW: Nice-to-have improvement

## 4. Positive Highlights
What did users love? What worked well?

## 5. Actionable Recommendations
Provide 3-5 specific, prioritized recommendations to improve the prototype based on the feedback.

Format your response in clear markdown with sections as shown above."""

GENERATE_TEST_SUMMARY_PROMPT = """You are a UX research analyst creating a summary report for the Test stage.

Project: {project_name}
Project Goal: {project_goal}

All Test Results:
{all_test_results}

Create a concise executive summary (2-3 paragraphs) that includes:
1. What was tested and with how many participants
2. Key findings (2-3 most important insights)
3. Overall assessment (validated features vs. issues found)
4. Recommended next steps (refine prototype, proceed to implementation, or re-test)

Keep it concise and actionable. Focus on insights that drive decisions."""
