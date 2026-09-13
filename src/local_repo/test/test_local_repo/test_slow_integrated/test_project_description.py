import os
import re

import requests

import protoprimer
from local_test.toml_handler import load_toml_data
from protoprimer.primer_kernel import ConfConstClient


def test_project_description():

    # given:

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

    toml_data = load_toml_data(toml_path)

    project_description = toml_data["project"]["description"]
    project_url = toml_data["project"]["urls"]["Repository"]

    # when:

    api_url = re.sub(
        r"^https://github\.com/",
        "https://api.github.com/repos/",
        project_url,
    )

    request_headers = {}
    # Request limits:
    # *   unauthenticated ~ 60/hour
    # *   authenticated ~ 1000/hour
    github_token = os.environ.get("GITHUB_TOKEN")
    if github_token is not None:
        request_headers["Authorization"] = f"Bearer {github_token}"

    api_response = requests.get(
        api_url,
        headers=request_headers,
    )
    api_response.raise_for_status()
    github_description = api_response.json()["description"]

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
    for text_shortcode, text_emoji in emoji_map.items():
        translated_description = translated_description.replace(
            text_shortcode,
            text_emoji,
        )

    # then:

    assert project_description == translated_description
