import os
import re
from unittest import TestCase

import requests

import protoprimer
from local_test.toml_handler import load_toml_data
from protoprimer.primer_kernel import ConfConstClient


class ThisTestClass(TestCase):

    def test_project_description(self):
        toml_path: str = str(
            os.path.join(
                # 4 levels up without basename to `src`: ../../../../../.
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(
                            os.path.dirname(
                                os.path.dirname(__file__),
                            ),
                        ),
                    ),
                ),
                protoprimer.__name__,
                ConfConstClient.default_pyproject_toml_basename,
            )
        )

        # when:

        toml_data = load_toml_data(toml_path)

        project_description = toml_data["project"]["description"]
        project_url = toml_data["project"]["urls"]["Repository"]

        api_url = re.sub(r"^https://github\.com/", "https://api.github.com/repos/", project_url)
        response = requests.get(api_url)
        response.raise_for_status()
        github_description = response.json()["description"]

        assert github_description is not None

        emoji_map = {
            ":sparkles:": "✨",
            ":boot:": "👢",
            ":bomb:": "💣",
            ":shield:": "🛡️",
            ":rocket:": "🚀",
            ":fast_forward:": "⏩",
        }

        translated_description = github_description
        for shortcode, emoji in emoji_map.items():
            translated_description = translated_description.replace(shortcode, emoji)

        self.assertEqual(
            project_description,
            translated_description,
        )
