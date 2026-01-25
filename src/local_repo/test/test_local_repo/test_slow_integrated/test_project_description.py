import os
from unittest import TestCase

import requests
from bs4 import BeautifulSoup

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

        # Fetch the HTML content from the URL:
        response = requests.get(project_url)
        response.raise_for_status()
        text_html = response.text

        parsed_html = BeautifulSoup(text_html, "html.parser")

        # Find the description from the "About" section:
        about_section = parsed_html.find("p", class_="f4 my-3")
        github_description = (
            about_section.get_text(strip=True) if about_section else None
        )

        assert github_description is not None

        emoji_map = {
            ":sparkles:": "✨",
            ":boot:": "👢",
            ":bomb:": "💣",
            ":shield:": "🛡️",
            ":rocket:": "🚀",
        }

        translated_description = project_description
        for shortcode, emoji in emoji_map.items():
            translated_description = translated_description.replace(shortcode, emoji)

        self.assertEqual(
            translated_description,
            github_description,
        )
