import pytest


class TestSampleOutput:
    @pytest.mark.parametrize(
        ('file_path', 'expected_snippet'),
        [
            ("output/203/index.html", "Version 2.03"),
            ("output/202/index.html", "Version 2.02"),
            ("output/201/index.html", "Version 2.01"),
        ]
    )
    def test_sample_output(self, file_path, expected_snippet):
        with open(file_path, "r") as open_file:
            file_contents = open_file.read()
            assert expected_snippet in file_contents