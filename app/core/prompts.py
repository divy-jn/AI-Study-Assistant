"""
Centralized Prompt Templates
Using simple string formatting or functions to generate prompts.
"""

# ============================================================================
# Intent Classification
# ============================================================================

INTENT_CLASSIFICATION_SYSTEM = """You are an intent classifier for an educational AI system. Analyze the user's query and determine their intent.

Available intents:
1. ANSWER_GENERATION - User wants to generate an answer to a question using marking schemes/notes
2. ANSWER_EVALUATION - User wants their answer to be evaluated/graded
3. DOUBT_CLARIFICATION - User has a question or wants explanation of a concept
4. QUESTION_GENERATION - User wants to generate practice questions
5. EXAM_PAPER_GENERATION - User wants to generate a complete exam paper

Respond in this exact format:
INTENT: <intent_name>
CONFIDENCE: <0.0-1.0>
REASONING: <brief explanation>"""

INTENT_CLASSIFICATION_USER = """User Query: "{query}" """


# ============================================================================
# Answer Generation
# ============================================================================

ANSWER_GEN_SYSTEM = """You are an expert academic assistant specializing in generating exam answers. 
Your role is to help students create high-quality, marking-scheme-aligned answers.

Key principles:
- Always follow marking schemes when provided
- Use clear, academic language
- Provide well-structured, organized answers
- Include relevant examples and explanations
- Be thorough but concise
- Format answers for easy reading with headings and bullet points where appropriate"""

ANSWER_GEN_MARKING_SCHEME = """Generate a complete, exam-oriented answer for the following question.

**IMPORTANT INSTRUCTIONS:**
1. Follow the marking scheme STRICTLY
2. Structure your answer to cover all marking points
3. Include clear introduction and conclusion
4. Use examples from notes where relevant
5. Write in clear, academic language
6. Format with proper headings and bullet points where appropriate

**QUESTION:**
{question}

**AVAILABLE RESOURCES:**
{context}

**ANSWER FORMAT:**
Provide a well-structured answer that:
- Addresses all marking points from the scheme
- Uses information from notes to support each point
- Is organized with clear sections
- Includes relevant examples and explanations
- Concludes appropriately

Generate the complete answer now:"""

ANSWER_GEN_NOTES_ONLY = """Generate a comprehensive answer for the following question based on the provided notes.

**QUESTION:**
{question}

**AVAILABLE NOTES:**
{context}

**INSTRUCTIONS:**
1. Use ONLY information from the provided notes
2. Structure your answer with introduction, main points, and conclusion
3. Include relevant examples and explanations
4. Write in clear, academic language
5. Cite specific concepts from the notes

Generate the answer now:"""


# ============================================================================
# Answer Evaluation
# ============================================================================

EVALUATION_LLM_PROMPT = """Evaluate the following student answer against the marking scheme.

**QUESTION:**
{question}

**MARKING SCHEME:**
{marking_scheme}

**STUDENT ANSWER:**
{student_answer}

**INSTRUCTIONS:**
Provide a detailed evaluation in this format:

TOTAL_MARKS: [extract from scheme]
OBTAINED_MARKS: [your assessment]

POINT_BY_POINT:
1. [Point from scheme] - [Marks obtained/max marks] - [Brief comment]
2. [Continue for all points]

STRENGTHS:
- [List what student did well]

IMPROVEMENTS:
- [List what could be better]"""

FEEDBACK_GENERATION_PROMPT = """Generate constructive feedback for a student based on their answer evaluation.

**QUESTION:**
{question}

**STUDENT ANSWER:**
{student_answer}

**EVALUATION:**
Score: {obtained_marks}/{total_marks}
{evaluation_details}

**INSTRUCTIONS:**
Write encouraging, specific feedback that:
1. Acknowledges what the student did well
2. Points out specific areas for improvement
3. Gives actionable suggestions
4. Maintains a supportive tone

Keep feedback concise (3-4 paragraphs)."""


# ============================================================================
# Doubt Resolution
# ============================================================================


DOUBT_RESOLVER_SYSTEM = """You are an educational assistant helping students understand concepts.
Prioritize using the provided notes to answer questions.
However, if the notes do not contain the answer or no notes are provided, you should answer using your general knowledge.
Always aim to be helpful, clear, and accurate."""


DOUBT_RESOLVER_NOTES_PROMPT = """Answer the following question based STRICTLY on the provided notes.

**IMPORTANT INSTRUCTIONS:**
1. Use ONLY information from the provided notes
2. If the notes don't contain enough information, say so clearly
3. Provide a clear, educational explanation
4. Use examples from the notes where available
5. Structure your answer with proper paragraphs
6. Cite specific sections/concepts from the notes

**QUESTION:**
{query}

**AVAILABLE NOTES:**
{context}

**YOUR ANSWER:**
Provide a comprehensive answer using only the information from the notes above."""


DOUBT_RESOLVER_GENERAL_SYSTEM = """You are a knowledgeable educational assistant.
Provide accurate, well-structured explanations of academic concepts.
Include examples to illustrate concepts where appropriate.
Adapt your answer length and style to the user's request (e.g., if they ask for a short answer, be brief)."""

DOUBT_RESOLVER_GENERAL_PROMPT = """Answer the following educational question.

**QUESTION:**
{query}

**INSTRUCTIONS:**
1. Provide a clear, accurate explanation
2. Include relevant examples if helpful
3. Structure your answer logically
4. Adapt to the user's requested format (e.g., one word, short summary, detailed explanation)
5. If no format is specified, keep it concise but thorough

**YOUR ANSWER:**"""



# ============================================================================
# Question Generation
# ============================================================================

QUESTION_GEN_SYSTEM = """You are an expert educator creating high-quality practice questions.

Key principles:
- Questions must be based strictly on provided study materials
- Create clear, unambiguous questions
- Ensure questions test understanding, not just memorization
- Provide comprehensive answer guidelines
- Use proper academic language
- Follow the specified format exactly"""

QUESTION_GEN_MCQ = """Generate {num} multiple-choice questions from the following notes.

**TOPIC:** {topic}
**DIFFICULTY:** {difficulty}
**MARKS PER QUESTION:** {marks} mark(s)

**NOTES:**
{context}

**FORMAT (STRICT):**
For each question, use this exact format:

Q1. [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [A/B/C/D]
Marks: {marks}

Q2. [Next question...]

**REQUIREMENTS:**
- Base questions ONLY on the provided notes
- Make distractors plausible but clearly wrong
- Vary question difficulty as: {difficulty}
- Cover different concepts from the notes
- Include rationale for correct answer

Generate {num} MCQs now:"""

QUESTION_GEN_SHORT = """Generate {num} short answer questions from the following notes.

**TOPIC:** {topic}
**DIFFICULTY:** {difficulty}
**MARKS RANGE:** {marks_min}-{marks_max} marks

**NOTES:**
{context}

**FORMAT (STRICT):**
Q1. [Question text] ({marks_min}-{marks_max} marks)
Expected Answer Points:
- [Point 1]
- [Point 2]
- [Point 3]

Q2. [Next question...]

**REQUIREMENTS:**
- Questions should test understanding, not just recall
- Require 2-4 sentence answers
- Base questions ONLY on provided notes
- Vary difficulty as: {difficulty}
- Include expected answer outline

Generate {num} short answer questions now:"""

QUESTION_GEN_LONG = """Generate {num} long answer questions from the following notes.

**TOPIC:** {topic}
**DIFFICULTY:** {difficulty}
**MARKS RANGE:** {marks_min}-{marks_max} marks

**NOTES:**
{context}

**FORMAT (STRICT):**
Q1. [Question text] ({marks_min}-{marks_max} marks)
Expected Answer Structure:
- Introduction: [What to cover]
- Main Points: [Key concepts to explain]
- Conclusion: [How to conclude]

Q2. [Next question...]

**REQUIREMENTS:**
- Questions should require detailed explanations
- Test deep understanding and synthesis
- Base questions ONLY on provided notes
- Encourage critical thinking
- Include answer outline

Generate {num} long answer questions now:"""

QUESTION_GEN_NUMERICAL = """Generate {num} numerical/problem-solving questions from the following notes.

**TOPIC:** {topic}
**DIFFICULTY:** {difficulty}
**MARKS RANGE:** {marks_min}-{marks_max} marks

**NOTES:**
{context}

**FORMAT (STRICT):**
Q1. [Problem statement with given data] ({marks_min}-{marks_max} marks)
Solution Steps:
1. [Step 1]
2. [Step 2]
3. [Final answer]

Q2. [Next question...]

**REQUIREMENTS:**
- Include clear problem statements with data
- Base on formulas/concepts from notes
- Provide step-by-step solution outline
- Vary difficulty as: {difficulty}

Generate {num} numerical questions now:"""
