import os
from unittest.mock import patch

from local_test.name_assertion import assert_test_module_name_embeds_str
from protoprimer.primer_kernel import (
    EnvContext,
    EnvVar,
    PackageDriverUv,
    PackageDriverPip,
)


def test_relationship():
    assert_test_module_name_embeds_str(EnvContext.__name__)


def test_init_default():
    # given:
    # when:
    env_ctx = EnvContext()
    # then:
    assert isinstance(env_ctx.package_driver, PackageDriverPip)


@patch.dict(os.environ, {EnvVar.var_PROTOPRIMER_USE_UV.value: "True"})
def test_init_with_uv():
    # given:
    # when:
    env_ctx = EnvContext()
    # then:
    assert isinstance(env_ctx.package_driver, PackageDriverUv)


@patch.dict(os.environ, {EnvVar.var_PROTOPRIMER_USE_UV.value: "False"})
def test_init_without_uv():
    # given:
    # when:
    env_ctx = EnvContext()
    # then:
    assert isinstance(env_ctx.package_driver, PackageDriverPip)
