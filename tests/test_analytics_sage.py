"""Tests for the Analytics Sage agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from app.agents import (
    AnalyticsSage,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import AnalyticsEngine, UsageMetrics

@pytest.mark.asyncio
async def test_usage_pattern_analysis(analytics_sage: AnalyticsSage):
    """Test usage pattern analysis capabilities."""
    # Create test analysis task
    analysis_task = AgentTask(
        task_id="test-analysis",
        task_type="analyze_usage_patterns",
        parameters={
            "time_range": {
                "start": datetime.now() - timedelta(days=30),
                "end": datetime.now()
            },
            "metrics": ["access_frequency", "search_patterns", "content_engagement"],
            "options": {
                "granularity": "daily",
                "user_segments": ["researchers", "students", "casual_readers"]
            }
        }
    )

    # Analyze patterns
    result = await analytics_sage._analyze_usage_patterns(analysis_task)

    # Verify analysis results
    assert result["status"] == "completed"
    assert "patterns" in result
    assert "metrics" in result
    assert "insights" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_knowledge_gap_identification(analytics_sage: AnalyticsSage):
    """Test knowledge gap identification capabilities."""
    # Create test gap task
    gap_task = AgentTask(
        task_id="test-gap",
        task_type="identify_knowledge_gaps",
        parameters={
            "content_areas": ["science", "technology", "engineering"],
            "criteria": {
                "coverage_threshold": 0.7,
                "depth_requirements": "intermediate",
                "recency_threshold": 90
            }
        }
    )

    # Identify gaps
    result = await analytics_sage._identify_knowledge_gaps(gap_task)

    # Verify gap results
    assert result["status"] == "completed"
    assert "gaps" in result
    assert "priority_scores" in result
    assert "recommendations" in result

@pytest.mark.asyncio
async def test_trend_analysis(analytics_sage: AnalyticsSage):
    """Test trend analysis capabilities."""
    # Create test trend task
    trend_task = AgentTask(
        task_id="test-trend",
        task_type="analyze_trends",
        parameters={
            "topic_areas": ["machine_learning", "data_science", "artificial_intelligence"],
            "time_range": {
                "start": datetime.now() - timedelta(days=180),
                "end": datetime.now()
            },
            "options": {
                "trend_types": ["emerging", "declining", "seasonal"],
                "confidence_threshold": 0.6
            }
        }
    )

    # Analyze trends
    result = await analytics_sage._analyze_trends(trend_task)

    # Verify trend results
    assert result["status"] == "completed"
    assert "trends" in result
    assert "confidence_scores" in result
    assert "visualizations" in result

@pytest.mark.asyncio
async def test_content_health_monitoring(analytics_sage: AnalyticsSage):
    """Test content health monitoring capabilities."""
    # Create test health task
    health_task = AgentTask(
        task_id="test-health",
        task_type="monitor_content_health",
        parameters={
            "content_types": ["articles", "tutorials", "references"],
            "metrics": ["freshness", "accuracy", "completeness", "engagement"],
            "thresholds": {
                "freshness_days": 180,
                "accuracy_score": 0.8,
                "engagement_rate": 0.4
            }
        }
    )

    # Monitor health
    result = await analytics_sage._monitor_content_health(health_task)

    # Verify health results
    assert result["status"] == "completed"
    assert "health_scores" in result
    assert "alerts" in result
    assert "improvement_suggestions" in result

@pytest.mark.asyncio
async def test_recommendation_generation(analytics_sage: AnalyticsSage):
    """Test recommendation generation capabilities."""
    # Create test recommendation task
    recommendation_task = AgentTask(
        task_id="test-recommend",
        task_type="generate_recommendations",
        parameters={
            "user_profile": {
                "interests": ["programming", "mathematics"],
                "expertise_level": "intermediate",
                "learning_history": ["python_basics", "linear_algebra"]
            },
            "options": {
                "max_recommendations": 5,
                "diversity_factor": 0.3,
                "personalization_weight": 0.7
            }
        }
    )

    # Generate recommendations
    result = await analytics_sage._generate_recommendations(recommendation_task)

    # Verify recommendation results
    assert result["status"] == "completed"
    assert "recommendations" in result
    assert "relevance_scores" in result
    assert "explanation" in result
    assert len(result["recommendations"]) <= 5

@pytest.mark.asyncio
async def test_error_handling(analytics_sage: AnalyticsSage):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="analytics_processor",
        receiver="analytics_sage",
        content={"error": "Analytics processing failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await analytics_sage._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "analytics_sage"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 