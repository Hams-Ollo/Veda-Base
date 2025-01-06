"""Tests for the Learning Companion agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents import (
    LearningCompanion,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import LearningPathGenerator, QuizGenerator

@pytest.mark.asyncio
async def test_learning_path_creation(learning_companion: LearningCompanion):
    """Test learning path creation capabilities."""
    # Create test learning path task
    path_task = AgentTask(
        task_id="test-path",
        task_type="create_learning_path",
        parameters={
            "user_profile": {
                "interests": ["machine_learning", "data_science"],
                "current_level": "intermediate",
                "learning_goals": ["master_deep_learning", "understand_nlp"],
                "time_commitment": "10_hours_per_week"
            },
            "options": {
                "path_length": "3_months",
                "include_milestones": True,
                "include_assessments": True,
                "adaptive_pacing": True
            }
        }
    )

    # Create learning path
    result = await learning_companion._create_learning_path(path_task)

    # Verify learning path results
    assert result["status"] == "completed"
    assert "learning_path" in result
    assert "milestones" in result
    assert "assessments" in result
    assert "estimated_duration" in result
    assert "prerequisites" in result

@pytest.mark.asyncio
async def test_progress_tracking(learning_companion: LearningCompanion):
    """Test progress tracking capabilities."""
    # Create test progress tracking task
    progress_task = AgentTask(
        task_id="test-progress",
        task_type="track_progress",
        parameters={
            "user_id": "test_user",
            "learning_path_id": "test_path",
            "completed_items": ["module1", "module2"],
            "assessment_results": {
                "quiz1": 0.85,
                "assignment1": 0.92
            },
            "tracking_options": {
                "track_time_spent": True,
                "track_engagement": True,
                "track_comprehension": True
            }
        }
    )

    # Track progress
    result = await learning_companion._track_progress(progress_task)

    # Verify progress tracking results
    assert result["status"] == "completed"
    assert "progress_metrics" in result
    assert "completion_rate" in result
    assert "performance_metrics" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_quiz_generation(learning_companion: LearningCompanion):
    """Test quiz generation capabilities."""
    # Create test quiz generation task
    quiz_task = AgentTask(
        task_id="test-quiz",
        task_type="generate_quiz",
        parameters={
            "topic": "machine_learning_basics",
            "difficulty_level": "intermediate",
            "quiz_options": {
                "num_questions": 10,
                "question_types": ["multiple_choice", "true_false", "short_answer"],
                "include_explanations": True,
                "adaptive_difficulty": True
            }
        }
    )

    # Generate quiz
    result = await learning_companion._generate_quiz(quiz_task)

    # Verify quiz generation results
    assert result["status"] == "completed"
    assert "questions" in result
    assert "answers" in result
    assert "explanations" in result
    assert len(result["questions"]) == 10

@pytest.mark.asyncio
async def test_concept_explanation(learning_companion: LearningCompanion):
    """Test concept explanation capabilities."""
    # Create test explanation task
    explanation_task = AgentTask(
        task_id="test-explain",
        task_type="explain_concept",
        parameters={
            "concept": "neural_networks",
            "user_level": "beginner",
            "explanation_options": {
                "include_examples": True,
                "include_analogies": True,
                "include_visuals": True,
                "depth": "comprehensive"
            }
        }
    )

    # Generate explanation
    result = await learning_companion._explain_concept(explanation_task)

    # Verify explanation results
    assert result["status"] == "completed"
    assert "explanation" in result
    assert "examples" in result
    assert "analogies" in result
    assert "visual_aids" in result

@pytest.mark.asyncio
async def test_study_recommendation(learning_companion: LearningCompanion):
    """Test study recommendation capabilities."""
    # Create test recommendation task
    recommendation_task = AgentTask(
        task_id="test-recommend",
        task_type="recommend_study",
        parameters={
            "user_profile": {
                "learning_style": "visual",
                "available_time": "2_hours",
                "current_topics": ["python", "data_structures"],
                "performance_history": {
                    "algorithms": 0.75,
                    "programming": 0.85
                }
            }
        }
    )

    # Generate recommendations
    result = await learning_companion._recommend_study(recommendation_task)

    # Verify recommendation results
    assert result["status"] == "completed"
    assert "study_plan" in result
    assert "resources" in result
    assert "time_allocation" in result
    assert "focus_areas" in result

@pytest.mark.asyncio
async def test_error_handling(learning_companion: LearningCompanion):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="quiz_generator",
        receiver="learning_companion",
        content={"error": "Quiz generation failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await learning_companion._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "learning_companion"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 