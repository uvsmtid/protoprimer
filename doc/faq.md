---
# Not in any `toctree` (hidden from the side menu) but still built, in the sitemap, and indexable:
orphan: true
seo_title: "protoprimer FAQ: set up a Python repo, config, alternatives"
---

```{eval-rst}
.. meta::
   :description: Answers to common problems: set up a Python repo with one command, run apps in a venv, pin dependencies, and compare protoprimer with shell scripts and uv.
   :keywords: protoprimer, faq, questions, bootstrap, python, venv, repo, setup
```

# FAQ

Short answers with links to the docs which explain each topic.

## How do I make a Python repo runnable for other people without writing setup instructions?

`protoprimer` is an arg-less one-liner that sets up an isolated environment for a repo clone: [intro][intro.md]. Why it exists: [why_primer][background_why_primer.md], [simple_bootstrap][UC_60_43_19_67.simple_bootstrap.md].

## How do I set up a Python project with a single command and no arguments?

Add `proto_kernel.py` to the repo and run it: [instant_scenario][FT_21_75_54_18.instant_scenario.md]. Step by step: [tutorial][tutorial_overview.md].

## How do I get the right Python version and a virtual environment created automatically?

`protoprimer` downloads the required `python` (with the `uv` driver), creates `venv`, installs dependencies, and then runs custom steps: [boot_env][FT_85_17_35_21.boot_env.md]. The whole flow: [bootstrap_process][FT_57_87_94_94.bootstrap_process.md], [python_executable][FT_72_45_12_06.python_executable.md]. Which tool can provision `python`: [venv_driver][FT_73_95_31_84.venv_driver.md].

## Do I need anything installed before running a bootstrap script, and which Python versions can it start from?

Only `python3` in `PATH` and a minimum `python` version: [bootstrap_precondition][FT_22_11_94_65.bootstrap_precondition.md], [supported_python_versions][FT_84_11_73_28.supported_python_versions.md].

## How can a setup script run before the project's dependencies and virtualenv exist?

That is the "chicken and egg" problem: [why_proto][background_why_proto.md], [proto_code][FT_90_65_67_62.proto_code.md].

## Should I commit a bootstrap script into my repo, and why would it be a copy rather than a dependency?

A copy makes any clone runnable without installing anything first: [why_primer][background_why_primer.md], [proto_kernel][FT_87_17_49_36.proto_kernel.md].

## How do I keep a committed bootstrap script up to date, and can I turn auto-update off?

Add `protoprimer` as a dependency: [enable_updates][tutorial_enable_updates.md], [generated_boilerplate][FT_56_85_65_41.generated_boilerplate.md]. Turning it off is planned: [conditional_auto_update][UC_52_87_82_92.conditional_auto_update.md].

## How do I stop a Python project from picking up packages from the global environment?

`protoprimer` runs `python` in isolated mode and uses only the dedicated `venv`: [isolated_python][FT_28_25_63_06.isolated_python.md], [context_isolation][FT_66_02_54_56.context_isolation.md], [no_stray_packages][UC_78_58_06_54.no_stray_packages.md], [no_installation_outside_venv][UC_88_09_19_74.no_installation_outside_venv.md].

## How do I run my Python app in its virtualenv without typing the interpreter and source paths?

Use an entry script: [start_app tutorial][tutorial_start_app.md], [start_app][FT_05_08_64_67.start_app.md], [entry_script][FT_75_87_82_46.entry_script.md], [boot_vs_start][FT_58_74_37_70.boot_vs_start.md].

## How do I run a command or open a shell inside a project's virtualenv without activating it by hand?

[venv_shell][FT_99_89_51_06.venv_shell.md], [pipe_to_execute_with_activated_venv][UC_36_72_11_12.pipe_to_execute_with_activated_venv.md], [run_under_venv][UC_90_98_17_93.run_under_venv.md].

## How do I keep the repo root clean of setup and config files?

[clean_repo_root][tutorial_clean_repo_root.md], [tree_shape][FT_59_95_81_63.tree_shape.md], [conf_leap][FT_89_41_35_82.conf_leap.md], [reusable_dir][FT_20_13_95_11.reusable_dir.md].

## How do I set up a Python monorepo or a nested project layout with several environments?

[form_nested_repo][tutorial_form_nested_repo.md], [monorepo_support][FT_32_61_30_43.monorepo_support.md]. Planned: [support_monorepo][UC_94_67_42_40.support_monorepo.md], [single_proto_kernel_per_repo][UC_39_44_27_45.single_proto_kernel_per_repo.md].

## How do I keep per-clone and per-environment settings separate from repo-wide settings?

[config][config.md], [global_vs_local][FT_23_37_64_44.global_vs_local.md], [local_env_link][FT_92_51_35_07.local_env_link.md], [config_format][FT_48_62_07_98.config_format.md].

## How do I see which config values were actually applied?

Run `./prime eval`: [effective_config][config.md#effective-config], [effective_config][FT_19_44_42_19.effective_config.md].

## How do I override defaults of a script that takes no command-line arguments?

Use env vars or the shebang line: [env_var][FT_08_92_69_92.env_var.md], [shebang_line][FT_02_89_37_65.shebang_line.md].

## How do I pin exact dependency versions for a reproducible environment?

[version_pinning][FT_98_06_56_18.version_pinning.md]. A generated lock file is planned: [requirements_lock][UC_44_82_07_30.requirements_lock.md].

## How do I recreate or upgrade a virtualenv from scratch?

[reset_env][FT_42_03_79_73.reset_env.md], [upgrade_venv][UC_61_12_90_59.upgrade_venv.md].

## Can I use `uv` or `pip` to create the virtualenv and install packages, and how do I choose?

[venv_driver][FT_73_95_31_84.venv_driver.md], [why_not_uv][background_why_not_uv.md]. Selecting the installer is planned: [installer_pip_vs_uv][UC_09_61_98_94.installer_pip_vs_uv.md].

## How do I install packages from a private repository or behind a corporate TLS proxy?

[private_artifact_repo][FT_17_41_51_83.private_artifact_repo.md], [intranet_certs][UC_29_95_32_02.intranet_certs.md].

## Why shouldn't I use a shell script to set up a Python project?

[why_not_shell][background_why_not_shell.md], [python_vs_shell][FT_44_72_60_67.python_vs_shell.md].

## How does a repo bootstrap differ from `uv`, `pyenv`, `mise`, `direnv`, Nix or Docker?

[alternative][alternative.md], [why_not_uv][background_why_not_uv.md]. Containers (planned): [container_friendly][UC_48_17_11_65.container_friendly.md].

## How do I add my own steps to a repo setup?

[DAG_extension][FT_74_10_40_33.DAG_extension.md], [extend_DAG][UC_10_80_27_57.extend_DAG.md], [exit_point][FT_07_55_61_77.exit_point.md].

## How do I call setup code or read its config from my own scripts?

[call_lib][FT_85_17_35_21.call_lib.md], [lib_access_to_config_data][UC_54_26_66_63.lib_access_to_config_data.md], [context_propagation][FT_96_50_58_75.context_propagation.md].

## How do I debug a failed setup?

[debugging_and_troubleshooting][UC_17_31_62_27.debugging_and_troubleshooting.md], [troubleshooting][FT_13_56_86_20.troubleshooting.md], [log_verbosity][FT_38_73_38_52.log_verbosity.md], [trace_mode][FT_41_45_81_49.trace_mode.md].

[FT_02_89_37_65.shebang_line.md]: feature_topic/FT_02_89_37_65.shebang_line.md
[FT_05_08_64_67.start_app.md]: feature_topic/FT_05_08_64_67.start_app.md
[FT_07_55_61_77.exit_point.md]: feature_topic/FT_07_55_61_77.exit_point.md
[FT_08_92_69_92.env_var.md]: feature_topic/FT_08_92_69_92.env_var.md
[FT_13_56_86_20.troubleshooting.md]: feature_topic/FT_13_56_86_20.troubleshooting.md
[FT_17_41_51_83.private_artifact_repo.md]: feature_topic/FT_17_41_51_83.private_artifact_repo.md
[FT_19_44_42_19.effective_config.md]: feature_topic/FT_19_44_42_19.effective_config.md
[FT_20_13_95_11.reusable_dir.md]: feature_topic/FT_20_13_95_11.reusable_dir.md
[FT_21_75_54_18.instant_scenario.md]: feature_topic/FT_21_75_54_18.instant_scenario.md
[FT_22_11_94_65.bootstrap_precondition.md]: feature_topic/FT_22_11_94_65.bootstrap_precondition.md
[FT_23_37_64_44.global_vs_local.md]: feature_topic/FT_23_37_64_44.global_vs_local.md
[FT_28_25_63_06.isolated_python.md]: feature_topic/FT_28_25_63_06.isolated_python.md
[FT_32_61_30_43.monorepo_support.md]: feature_topic/FT_32_61_30_43.monorepo_support.md
[FT_38_73_38_52.log_verbosity.md]: feature_topic/FT_38_73_38_52.log_verbosity.md
[FT_41_45_81_49.trace_mode.md]: feature_topic/FT_41_45_81_49.trace_mode.md
[FT_42_03_79_73.reset_env.md]: feature_topic/FT_42_03_79_73.reset_env.md
[FT_44_72_60_67.python_vs_shell.md]: feature_topic/FT_44_72_60_67.python_vs_shell.md
[FT_48_62_07_98.config_format.md]: feature_topic/FT_48_62_07_98.config_format.md
[FT_56_85_65_41.generated_boilerplate.md]: feature_topic/FT_56_85_65_41.generated_boilerplate.md
[FT_57_87_94_94.bootstrap_process.md]: feature_topic/FT_57_87_94_94.bootstrap_process.md
[FT_58_74_37_70.boot_vs_start.md]: feature_topic/FT_58_74_37_70.boot_vs_start.md
[FT_59_95_81_63.tree_shape.md]: feature_topic/FT_59_95_81_63.tree_shape.md
[FT_66_02_54_56.context_isolation.md]: feature_topic/FT_66_02_54_56.context_isolation.md
[FT_72_45_12_06.python_executable.md]: feature_topic/FT_72_45_12_06.python_executable.md
[FT_73_95_31_84.venv_driver.md]: feature_topic/FT_73_95_31_84.venv_driver.md
[FT_74_10_40_33.DAG_extension.md]: feature_topic/FT_74_10_40_33.DAG_extension.md
[FT_75_87_82_46.entry_script.md]: feature_topic/FT_75_87_82_46.entry_script.md
[FT_84_11_73_28.supported_python_versions.md]: feature_topic/FT_84_11_73_28.supported_python_versions.md
[FT_85_17_35_21.boot_env.md]: feature_topic/FT_85_17_35_21.boot_env.md
[FT_85_17_35_21.call_lib.md]: feature_topic/FT_85_17_35_21.call_lib.md
[FT_87_17_49_36.proto_kernel.md]: feature_topic/FT_87_17_49_36.proto_kernel.md
[FT_89_41_35_82.conf_leap.md]: feature_topic/FT_89_41_35_82.conf_leap.md
[FT_90_65_67_62.proto_code.md]: feature_topic/FT_90_65_67_62.proto_code.md
[FT_92_51_35_07.local_env_link.md]: feature_topic/FT_92_51_35_07.local_env_link.md
[FT_96_50_58_75.context_propagation.md]: feature_topic/FT_96_50_58_75.context_propagation.md
[FT_98_06_56_18.version_pinning.md]: feature_topic/FT_98_06_56_18.version_pinning.md
[FT_99_89_51_06.venv_shell.md]: feature_topic/FT_99_89_51_06.venv_shell.md
[UC_09_61_98_94.installer_pip_vs_uv.md]: use_case/UC_09_61_98_94.installer_pip_vs_uv.md
[UC_10_80_27_57.extend_DAG.md]: use_case/UC_10_80_27_57.extend_DAG.md
[UC_17_31_62_27.debugging_and_troubleshooting.md]: use_case/UC_17_31_62_27.debugging_and_troubleshooting.md
[UC_29_95_32_02.intranet_certs.md]: use_case/UC_29_95_32_02.intranet_certs.md
[UC_36_72_11_12.pipe_to_execute_with_activated_venv.md]: use_case/UC_36_72_11_12.pipe_to_execute_with_activated_venv.md
[UC_39_44_27_45.single_proto_kernel_per_repo.md]: use_case/UC_39_44_27_45.single_proto_kernel_per_repo.md
[UC_44_82_07_30.requirements_lock.md]: use_case/UC_44_82_07_30.requirements_lock.md
[UC_48_17_11_65.container_friendly.md]: use_case/UC_48_17_11_65.container_friendly.md
[UC_52_87_82_92.conditional_auto_update.md]: use_case/UC_52_87_82_92.conditional_auto_update.md
[UC_54_26_66_63.lib_access_to_config_data.md]: use_case/UC_54_26_66_63.lib_access_to_config_data.md
[UC_60_43_19_67.simple_bootstrap.md]: use_case/UC_60_43_19_67.simple_bootstrap.md
[UC_61_12_90_59.upgrade_venv.md]: use_case/UC_61_12_90_59.upgrade_venv.md
[UC_78_58_06_54.no_stray_packages.md]: use_case/UC_78_58_06_54.no_stray_packages.md
[UC_88_09_19_74.no_installation_outside_venv.md]: use_case/UC_88_09_19_74.no_installation_outside_venv.md
[UC_90_98_17_93.run_under_venv.md]: use_case/UC_90_98_17_93.run_under_venv.md
[UC_94_67_42_40.support_monorepo.md]: use_case/UC_94_67_42_40.support_monorepo.md
[alternative.md]: alternative.md
[background_why_not_shell.md]: background_why_not_shell.md
[background_why_not_uv.md]: background_why_not_uv.md
[background_why_primer.md]: background_why_primer.md
[background_why_proto.md]: background_why_proto.md
[config.md]: config.md
[config.md#effective-config]: config.md#effective-config
[intro.md]: intro.md
[tutorial_clean_repo_root.md]: tutorial_clean_repo_root.md
[tutorial_enable_updates.md]: tutorial_enable_updates.md
[tutorial_form_nested_repo.md]: tutorial_form_nested_repo.md
[tutorial_overview.md]: tutorial_overview.md
[tutorial_start_app.md]: tutorial_start_app.md
