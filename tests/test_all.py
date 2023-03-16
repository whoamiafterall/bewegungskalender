from post_caldav_events.main import main
import os

def test_configs():
    config_dir = "tests/configs"
    configs = [f for f in os.listdir(config_dir) if f.endswith(".yml")]
    for c in configs:
        print("testing " + c)
        config_file = config_dir + "/" + c
        with open(config_file + ".out", 'r') as f:
            expected_output = f.read()
        assert main(["--config", config_file]) == expected_output
