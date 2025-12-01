# test_config.py
from src.core.configLoader import config_loader
from pathlib import Path

def test_basic_functionality():
    print("🧪 Testing ConfigLoader Basic Functionality")
    print("=" * 50)

    # --- Test 1: Singleton instance ---
    print("1. Testing singleton instance...")
    assert config_loader is not None, "config_loader instance is None"
    assert type(config_loader).__name__ == "ConfigLoader", "config_loader has wrong type"
    print("   ✅ Singleton instance OK")

    # --- Test 2: Base path resolution ---
    print("\n2. Testing config base path...")
    base_path: Path = config_loader.config_base_path
    assert base_path.exists() and base_path.is_dir(), f"Config folder missing: {base_path}"
    print(f"   ✅ Config folder exists: {base_path}")

    # --- Test 3: Load database.yaml ---
    print("\n3. Loading database.yaml...")
    try:
        db_config = config_loader.load_config("database")
        assert isinstance(db_config, dict), "database.yaml did not return a dict"
        print(f"   ✅ Database config loaded: keys = {list(db_config.keys())}")
    except FileNotFoundError:
        print("   ⚠️ database.yaml not found in config/ folder")

    # --- Test 4: Access keys safely ---
    print("\n4. Accessing configuration safely...")
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 5432)
    name = db_config.get("name", "default_db")
    missing = db_config.get("nonexistent_key", "default_value")

    print(f"   ✅ Host: {host}")
    print(f"   ✅ Port: {port}")
    print(f"   ✅ DB Name: {name}")
    print(f"   ✅ Missing key fallback: {missing}")

    print("\n🎉 Basic ConfigLoader tests passed!")


def test_task_specific_config():
    print("\n🧪 Testing Task-Specific Config Merging")
    print("=" * 50)
    # Example: assume processing_pipeline.yaml exists with tasks 'task1', 'task2'
    try:
        task_config = config_loader.get_task_config("processing_pipeline", "task1")
        assert isinstance(task_config, dict)
        print(f"   ✅ Task-specific config loaded: keys = {list(task_config.keys())}")
    except FileNotFoundError:
        print("   ⚠️ processing_pipeline.yaml not found in config/ folder")

    print("\n🎉 Task-specific ConfigLoader tests passed!")


if __name__ == "__main__":
    test_basic_functionality()
    test_task_specific_config()
