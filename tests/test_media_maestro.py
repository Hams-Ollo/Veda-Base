"""Tests for the Media Maestro agent."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pathlib import Path

from app.agents import (
    MediaMaestro,
    AgentMessage,
    AgentTask,
    MessageType,
    Priority
)
from app.core import MediaProcessor, TranscriptionEngine

@pytest.mark.asyncio
async def test_image_analysis(media_maestro: MediaMaestro):
    """Test image analysis capabilities."""
    # Create test image analysis task
    image_task = AgentTask(
        task_id="test-image",
        task_type="analyze_image",
        parameters={
            "image_path": "test_image.jpg",
            "analysis_options": {
                "detect_objects": True,
                "extract_text": True,
                "analyze_composition": True,
                "identify_colors": True,
                "recognize_faces": True
            }
        }
    )

    # Analyze image
    result = await media_maestro._analyze_image(image_task)

    # Verify image analysis results
    assert result["status"] == "completed"
    assert "objects" in result
    assert "text_content" in result
    assert "composition_analysis" in result
    assert "color_palette" in result
    assert "metadata" in result

@pytest.mark.asyncio
async def test_audio_transcription(media_maestro: MediaMaestro):
    """Test audio transcription capabilities."""
    # Create test transcription task
    transcription_task = AgentTask(
        task_id="test-audio",
        task_type="transcribe_audio",
        parameters={
            "audio_path": "test_audio.mp3",
            "transcription_options": {
                "language": "en",
                "speaker_diarization": True,
                "include_timestamps": True,
                "detect_emotions": True
            }
        }
    )

    # Transcribe audio
    result = await media_maestro._transcribe_audio(transcription_task)

    # Verify transcription results
    assert result["status"] == "completed"
    assert "transcript" in result
    assert "speakers" in result
    assert "timestamps" in result
    assert "emotions" in result

@pytest.mark.asyncio
async def test_video_processing(media_maestro: MediaMaestro):
    """Test video processing capabilities."""
    # Create test video processing task
    video_task = AgentTask(
        task_id="test-video",
        task_type="process_video",
        parameters={
            "video_path": "test_video.mp4",
            "processing_options": {
                "extract_frames": True,
                "analyze_motion": True,
                "generate_thumbnails": True,
                "scene_detection": True,
                "extract_audio": True
            }
        }
    )

    # Process video
    result = await media_maestro._process_video(video_task)

    # Verify video processing results
    assert result["status"] == "completed"
    assert "frames" in result
    assert "motion_analysis" in result
    assert "thumbnails" in result
    assert "scenes" in result
    assert "audio_track" in result

@pytest.mark.asyncio
async def test_media_tagging(media_maestro: MediaMaestro):
    """Test media tagging capabilities."""
    # Create test tagging task
    tagging_task = AgentTask(
        task_id="test-tagging",
        task_type="tag_media",
        parameters={
            "media_items": [
                {"type": "image", "path": "image1.jpg"},
                {"type": "video", "path": "video1.mp4"}
            ],
            "tagging_options": {
                "content_tags": True,
                "technical_metadata": True,
                "semantic_labels": True,
                "auto_categorization": True
            }
        }
    )

    # Tag media
    result = await media_maestro._tag_media(tagging_task)

    # Verify tagging results
    assert result["status"] == "completed"
    assert "content_tags" in result
    assert "technical_metadata" in result
    assert "semantic_labels" in result
    assert "categories" in result

@pytest.mark.asyncio
async def test_media_search(media_maestro: MediaMaestro):
    """Test media search capabilities."""
    # Create test search task
    search_task = AgentTask(
        task_id="test-search",
        task_type="search_media",
        parameters={
            "query": "nature landscape",
            "search_options": {
                "media_types": ["image", "video"],
                "min_resolution": "1080p",
                "date_range": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                },
                "similarity_threshold": 0.7
            }
        }
    )

    # Search media
    result = await media_maestro._search_media(search_task)

    # Verify search results
    assert result["status"] == "completed"
    assert "matches" in result
    assert "similarity_scores" in result
    assert "filtered_results" in result
    assert "search_metadata" in result

@pytest.mark.asyncio
async def test_error_handling(media_maestro: MediaMaestro):
    """Test error handling capabilities."""
    # Create test error message
    error_message = AgentMessage(
        message_id="test-error",
        message_type=MessageType.ERROR,
        sender="media_processor",
        receiver="media_maestro",
        content={"error": "Media processing failed"},
        priority=Priority.HIGH
    )

    # Handle error
    response = await media_maestro._handle_error(error_message)

    # Verify error handling
    assert response.message_type == MessageType.RESPONSE
    assert response.sender == "media_maestro"
    assert response.content["status"] == "error_handled"
    assert "recovery_action" in response.content 