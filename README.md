# Medical AI Safety Middleware for Diabetes-Related Questions

Academic prototype demonstrating real-time claim verification, hallucination detection, and medical risk mitigation on Groq LLM generations.

## Key Features

- AI-powered medical response generation
- Claim-level hallucination detection
- Evidence-based claim verification
- Semantic similarity analysis
- Unsafe medical advice detection
- Emergency response detection
- Risk scoring and classification
- Medical response safety evaluation
- React-based user interface
- Backend API integration

## Safety Mechanism

MedGuard AI analyzes AI-generated medical responses by checking claims,
evaluating supporting evidence, identifying potentially unsafe advice,
and assigning a risk level to help users recognize unreliable responses.

## Disclaimer

MedGuard AI is an academic project and is not a substitute for
professional medical advice, diagnosis, or treatment.

## System Workflow

1. User submits a medical question.
2. The AI generates a medical response.
3. The response is divided into individual claims.
4. Claims are analyzed using semantic similarity and verification techniques.
5. Medical safety rules identify potentially unsafe recommendations.
6. Emergency-related content is checked using safety mechanisms.
7. A risk score is calculated based on detected issues.
8. Claims are categorized based on their verification status.
9. The system generates a safety analysis of the response.
10. The verified response and risk information are displayed in the frontend.

## Core Components

- AI Response Generation
- Claim Extraction
- Hallucination Detection
- Evidence-Based Verification
- Semantic Similarity Analysis
- Medical Safety Rules
- Emergency Detection
- Risk Classification
- Response Evaluation
- Frontend Visualization

## Technologies Used

- Python
- Flask
- React.js
- Groq API
- Sentence Transformers
- Machine Learning
- SQLite
- JavaScript
- CSS
- REST API

## Project Objectives

- Identify potentially unsupported medical claims.
- Improve transparency in AI-generated medical responses.
- Detect potentially unsafe medical recommendations.
- Evaluate response reliability using automated techniques.
- Provide understandable safety feedback to users.

## Future Improvements

- Expand medical evidence sources.
- Improve claim verification accuracy.
- Enhance medical safety evaluation.
- Add more comprehensive test cases.
- Improve risk scoring and explainability.
- Support additional medical question categories.
- Improve frontend visualization.
- Optimize response processing.
- Add detailed evaluation reports.
- Explore advanced LLM evaluation techniques.

## Limitations

- Verification results depend on available evidence and detection methods.
- Semantic similarity does not guarantee medical correctness.
- Rule-based detection may miss complex medical risks.
- AI-generated responses can still contain inaccurate information.
- The system is an academic prototype and requires further validation.

## Disclaimer

MedGuard AI is developed for academic and research purposes.
It is not intended to provide medical advice, diagnosis, or treatment.
Users should consult qualified healthcare professionals for medical concerns.