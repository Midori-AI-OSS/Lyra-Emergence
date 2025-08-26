"""Tests for model recommendation system."""

from src.config.model_recommendations import (
    MODEL_DATABASE,
    get_model_info,
    get_models_by_category,
    recommend_model,
)


class TestModelRecommendations:
    """Test model recommendation system."""

    def test_get_models_by_category_small(self):
        """Test retrieving small models."""
        small_models = get_models_by_category("small")
        assert len(small_models) > 0
        assert all(model.size_category == "small" for model in small_models)

    def test_get_models_by_category_medium(self):
        """Test retrieving medium models."""
        medium_models = get_models_by_category("medium")
        assert len(medium_models) > 0
        assert all(model.size_category == "medium" for model in medium_models)

    def test_get_models_by_category_large(self):
        """Test retrieving large models."""
        large_models = get_models_by_category("large")
        assert len(large_models) > 0
        assert all(model.size_category == "large" for model in large_models)

    def test_recommend_model_small_system(self):
        """Test model recommendation for small system."""
        # 4GB RAM, no GPU
        recommended = recommend_model(4.0, 0.0)
        assert recommended is not None
        assert recommended.size_category == "small"
        assert recommended.min_ram_gb <= 4.0

    def test_recommend_model_medium_system(self):
        """Test model recommendation for medium system."""
        # 16GB RAM, 8GB VRAM
        recommended = recommend_model(16.0, 8.0)
        assert recommended is not None
        # Should be able to recommend medium or large model
        assert recommended.min_ram_gb <= 16.0
        assert recommended.min_vram_gb <= 8.0

    def test_recommend_model_large_system(self):
        """Test model recommendation for large system."""
        # 64GB RAM, 40GB VRAM - prefer performance (realistic for modern large models)
        recommended = recommend_model(64.0, 40.0, prefer_performance=True)
        assert recommended is not None
        assert recommended.min_ram_gb <= 64.0
        assert recommended.min_vram_gb <= 40.0

    def test_recommend_model_insufficient_resources(self):
        """Test model recommendation with insufficient resources."""
        # Very low resources
        recommended = recommend_model(1.0, 0.0)
        # Should still try to recommend something or return None
        if recommended:
            assert recommended.min_ram_gb <= 1.0 or recommended.quantization_support

    def test_get_model_info_exists(self):
        """Test retrieving info for existing model."""
        model_info = get_model_info("Qwen/Qwen2.5-7B-Instruct")
        assert model_info is not None
        assert model_info.model_id == "Qwen/Qwen2.5-7B-Instruct"

    def test_get_model_info_not_exists(self):
        """Test retrieving info for non-existent model."""
        model_info = get_model_info("nonexistent/model")
        assert model_info is None

    def test_model_database_integrity(self):
        """Test that model database has proper structure."""
        assert len(MODEL_DATABASE) > 0

        for model in MODEL_DATABASE:
            assert model.model_id
            assert model.size_category in ["small", "medium", "large"]
            assert model.parameter_count
            assert model.min_ram_gb > 0
            assert model.min_vram_gb >= 0
            assert model.recommended_ram_gb >= model.min_ram_gb
            assert model.recommended_vram_gb >= model.min_vram_gb
            assert isinstance(model.quantization_support, list)
            assert model.description
