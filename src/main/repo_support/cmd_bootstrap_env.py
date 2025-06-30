from __future__ import annotations

import logging

from protoprimer.primer_kernel import (
    EnvContext,
    main,
    TargetState,
)

logger = logging.getLogger()


def custom_main():
    main(customize_env_context)


def customize_env_context():
    # NOTE: It does not really customize anything:
    env_ctx = EnvContext()
    env_ctx.universal_sink = TargetState.target_full_proto_bootstrap
    return env_ctx


if __name__ == "__main__":
    custom_main()
