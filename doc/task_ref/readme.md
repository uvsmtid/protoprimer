NOTE: AI-generated

## Purpose

Every `TODO` in [primer_kernel.py][primer_kernel.py] is associated with a file under `doc/task_ref/`.

All `TODO`-s are grouped by similarity (by meaning).
Each group gets its own `TODO_*.md` file.
In addition to the in-place text,
the file gives a wider explanation with links to associated docs and other `TODO_*.md` files.

There are no "unrelated" `TODO`-s:
a `TODO` which does not fit any group is a group of one and gets its own `TODO_*.md` file.

## Conventions

*   Create a new `TODO_*.md` file for one group at a time:

    Generate its tag only after the file for the previous tag is created:

    ```shell
    ./cmd/gen_next_doc_id doc/task_ref
    ```

*   Associate the in-place `TODO`-s with the file (only after the file exists):

    Keep the original `TODO` text as is and add a comment line above it (with the same indentation):

    ```python
    # TODO: TODO_NN_NN_NN_NN.some_semantic_name.md:
    # TODO: <original text stays here>
    ```

*   Update the sub-sections below (the number of references) after each step.

*   A `TODO` already associated with another doc (e.g. `FT_*` or `UC_*` - not under `doc/task_ref/`) needs no additional `TODO_*.md` file.

*   A `TODO` directly under an already tagged `TODO` (the same block) is not tagged again.

*   Inside a docstring, the tag line has the same form but without the leading `#`:

    ```python
    """
    TODO: TODO_NN_NN_NN_NN.some_semantic_name.md:
    TODO: <original text stays here>
    """
    ```

*   Before creating a new `TODO_*.md` file, check the existing ones (to avoid duplicating the same issue):

    Group `TODO`-s by what they try to do (by meaning), not by the wording of the comment.

## Status

The number of references is the number of lines in `primer_kernel.py` with `TODO` mentioning the file.

The counts in `References` of existing files are current (initial counts are in parentheses where they changed).
Initially there were ~55 bare `TODO`-s: all of them are now associated (see below).

### Existing `TODO_*.md` files

#### [TODO_04_67_81_16.refactor_reusable_dirs.md][TODO_04_67_81_16.refactor_reusable_dirs.md]

References: 7 (initial: 2)

#### [TODO_19_13_09_01.propagate_start_sub_command_cli_args.md][TODO_19_13_09_01.propagate_start_sub_command_cli_args.md]

References: 1

#### [TODO_21_72_88_59.use_factory_to_avoid_running_boot_env_related_states.md][TODO_21_72_88_59.use_factory_to_avoid_running_boot_env_related_states.md]

References: 7

#### [TODO_41_10_50_01.implement_env_selector.md][TODO_41_10_50_01.implement_env_selector.md]

References: 6 (3 more bare `TODO` lines in the `python_selector_module` block are covered by block adjacency)

#### [TODO_47_08_90_90.propagate_exec_operation_for_func_call_lib.md][TODO_47_08_90_90.propagate_exec_operation_for_func_call_lib.md]

References: 2

#### [TODO_50_98_96_87.support_windows.md][TODO_50_98_96_87.support_windows.md]

References: 1

#### [TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md][TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md]

References: 4 (initial: 2)

#### [TODO_73_71_31_84.exec_operation_check_or_info.md][TODO_73_71_31_84.exec_operation_check_or_info.md]

References: 3 (initial: 2)

#### [TODO_91_75_37_57.implement_shebang_update.md][TODO_91_75_37_57.implement_shebang_update.md]

References: 1

#### Not referenced from `primer_kernel.py` (0 references)

*   [TODO_03_22_24_33.consolidate_exec_operation_and_entry_func_docs.md][TODO_03_22_24_33.consolidate_exec_operation_and_entry_func_docs.md]
*   [TODO_18_22_12_97.run_all_tests_under_min_python.md][TODO_18_22_12_97.run_all_tests_under_min_python.md]
*   [TODO_60_63_68_81.refactor_DAG_builder.md][TODO_60_63_68_81.refactor_DAG_builder.md] (KIV only: moved to `FT_77_15_06_50`)
*   [TODO_89_47_85_02.implement_env_selection.md][TODO_89_47_85_02.implement_env_selection.md]

### Associated with other docs (not under `doc/task_ref/`)

*   `FT_77_15_06_50.dynamic_DAG.md`: 13 references
*   `UC_81_50_97_17.do_not_reuse_logger.md`: 2 references
*   `UC_52_87_82_92.conditional_auto_update.md`: 1 reference
*   `FT_02_89_37_65.shebang_line.md`: 1 reference (together with `TODO_91_75_37_57`)

### New `TODO_*.md` files (for groups of bare `TODO`-s)

All proposed groups are created (and linked below) - every `TODO` in `primer_kernel.py` is now associated with a file.
Tags were generated one at a time (only when the file was created).
Line numbers are from the initial snapshot (they shifted after tag lines were added above the `TODO`-s).

#### New files (one per group)

1.  [TODO_39_94_67_54.rename_client_env_to_global_local.md][TODO_39_94_67_54.rename_client_env_to_global_local.md] (created): 6 refs

    *   207, 212, 220: `ConfLeap` `leap_client`/`leap_env` -> `global`/`local`; `leap_global`/`leap_local` consolidation.
    *   357: `ConfDst` naming (conf src vs conf dst).
    *   416, 421: `path_conf_client` -> `path_global_conf`; `path_conf_env` -> `path_local_conf`.
    *   Related: `FT_23_37_64_44.global_vs_local.md`, `FT_89_41_35_82.conf_leap.md`.

2.  [TODO_20_07_74_69.configure_dirs_at_client_level.md][TODO_20_07_74_69.configure_dirs_at_client_level.md] (created): 7 refs

    *   5088, 5091, 5094, 5097, 5100: `log`, `tmp`, `venv`, ... dirs should be configured at client level.
    *   866: take `uv.venv` name from config (or default constant).
    *   3537: do not use default values directly - resolve at the prev|next step.
    *   Related: [TODO_04_67_81_16.refactor_reusable_dirs.md][TODO_04_67_81_16.refactor_reusable_dirs.md].

3.  [TODO_87_26_62_66.clean_up_venv_driver_args.md][TODO_87_26_62_66.clean_up_venv_driver_args.md] (created): 8 refs

    *   780, 825, 837, 924, 975, 995: is the `venv` path arg needed given `state_local_venv_dir_abs_path_inited`?
    *   986, 1007: clean up `venv_python_file_abs_path` arg (use simple relative `${venv_abs_path}/bin/python`).

4.  [TODO_99_29_89_80.warn_only_when_conf_is_required.md][TODO_99_29_89_80.warn_only_when_conf_is_required.md] (created): 3 tag lines (4 TODO lines: the last two are in one block)

    *   2947, 3107, 3397, 3398: detect the min scenario and avoid the missing conf file warning (but still warn when required for some fields).

5.  [TODO_74_35_76_27.shell_driver_fallback_to_sh.md][TODO_74_35_76_27.shell_driver_fallback_to_sh.md] (created): 3 refs

    *   1209, 1212, 1215: `ShellDriverSh` and the fallback to `/bin/sh` (no `bash`, no `SHELL`).
    *   1212 (Windows without `shutil`/POSIX shell) also relates to [TODO_50_98_96_87.support_windows.md][TODO_50_98_96_87.support_windows.md].

6.  [TODO_68_40_26_10.define_env_vars_in_known_env_var_enum.md][TODO_68_40_26_10.define_env_vars_in_known_env_var_enum.md] (created): 2 refs

    *   1194 (`ZDOTDIR`), 1203 (`SHELL`): define in `KnownEnvVar` enum.

7.  [TODO_49_40_51_46.rename_state_names_to_final.md][TODO_49_40_51_46.rename_state_names_to_final.md] (created): 2 refs

    *   5135 ("reached" sounds weird), 5138 (rename according to the final name).

Single-entry groups (one file each):

*   [TODO_65_18_47_30.uv_bootstrap_venv_python_version.md][TODO_65_18_47_30.uv_bootstrap_venv_python_version.md] (created): 886 (assert `python` version is suitable for `uv`).
*   [TODO_25_82_21_54.rename_is_app_flag.md][TODO_25_82_21_54.rename_is_app_flag.md] (created): 5253 (`_is_app` is confusing).
*   [TODO_90_53_85_78.proto_dir_path_name.md][TODO_90_53_85_78.proto_dir_path_name.md] (created): 406, 407 (suffix `dir` clash; use in naming states): 2 refs.
*   [TODO_56_99_72_68.feature_topic_for_ref_root.md][TODO_56_99_72_68.feature_topic_for_ref_root.md] (created): 410 (add `feature_topic` for `ref root`).
*   [TODO_16_35_39_74.simplify_input_based_default.md][TODO_16_35_39_74.simplify_input_based_default.md] (created): 1277 (use lambdas instead of `None`).
*   [TODO_32_41_01_30.review_default_client_conf_file_rel_path.md][TODO_32_41_01_30.review_default_client_conf_file_rel_path.md] (created): 1371 (still needed if conf file base name is propagated?).
*   [TODO_79_50_81_23.use_constant_for_dst_dir_name.md][TODO_79_50_81_23.use_constant_for_dst_dir_name.md] (created): 1390 (use constant instead of `"dst"`).
*   [TODO_80_28_71_21.review_env_clean_up_after_isolated_mode.md][TODO_80_28_71_21.review_env_clean_up_after_isolated_mode.md] (created): 2675.
*   [TODO_05_17_21_85.review_parent_states_list.md][TODO_05_17_21_85.review_parent_states_list.md] (created): 3838 (needed given `derived_data_env_states`?).
*   [TODO_43_30_90_54.configure_max_file_log_level.md][TODO_43_30_90_54.configure_max_file_log_level.md] (created): 5652.
*   [TODO_69_28_79_76.skip_exec_argv_args_with_same_value.md][TODO_69_28_79_76.skip_exec_argv_args_with_same_value.md] (created): 5769 (maybe related to [TODO_19_13_09_01.propagate_start_sub_command_cli_args.md][TODO_19_13_09_01.propagate_start_sub_command_cli_args.md]).
*   [TODO_15_25_41_72.convert_selected_python_to_base_python.md][TODO_15_25_41_72.convert_selected_python_to_base_python.md] (created): 5998.
*   [TODO_71_33_38_11.override_proto_kernel_abs_path_in_conf_getter.md][TODO_71_33_38_11.override_proto_kernel_abs_path_in_conf_getter.md] (created): 6292.

#### Matches to existing files (no new file; done)

A bare `TODO` directly under an already tagged `TODO` (the same block) is not tagged again: 294 and 6145, 6146 (and the `use constants` line).

*   [TODO_04_67_81_16.refactor_reusable_dirs.md][TODO_04_67_81_16.refactor_reusable_dirs.md]: 553, 557, 561, 565 (combine by parent dir `./var`), 863 (relative to `cache/venv`).
*   [TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md][TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md]: 426 (rename `link_name` to `lconf_link`), 1385 (is `default_dir_rel_path_leap_env_link_name` used?).
*   [TODO_73_71_31_84.exec_operation_check_or_info.md][TODO_73_71_31_84.exec_operation_check_or_info.md]: 294 (second `TODO: implement?` line), 5118 (replaceable `env_check` step).
*   [TODO_41_10_50_01.implement_env_selector.md][TODO_41_10_50_01.implement_env_selector.md]: 6145, 6146 (same block as the already tagged 6144).

[primer_kernel.py]: ../../src/protoprimer/main/protoprimer/primer_kernel.py
[TODO_03_22_24_33.consolidate_exec_operation_and_entry_func_docs.md]: TODO_03_22_24_33.consolidate_exec_operation_and_entry_func_docs.md
[TODO_04_67_81_16.refactor_reusable_dirs.md]: TODO_04_67_81_16.refactor_reusable_dirs.md
[TODO_18_22_12_97.run_all_tests_under_min_python.md]: TODO_18_22_12_97.run_all_tests_under_min_python.md
[TODO_19_13_09_01.propagate_start_sub_command_cli_args.md]: TODO_19_13_09_01.propagate_start_sub_command_cli_args.md
[TODO_21_72_88_59.use_factory_to_avoid_running_boot_env_related_states.md]: TODO_21_72_88_59.use_factory_to_avoid_running_boot_env_related_states.md
[TODO_41_10_50_01.implement_env_selector.md]: TODO_41_10_50_01.implement_env_selector.md
[TODO_47_08_90_90.propagate_exec_operation_for_func_call_lib.md]: TODO_47_08_90_90.propagate_exec_operation_for_func_call_lib.md
[TODO_50_98_96_87.support_windows.md]: TODO_50_98_96_87.support_windows.md
[TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md]: TODO_53_40_17_68.default_env_config_vs_lconf_symlink.md
[TODO_60_63_68_81.refactor_DAG_builder.md]: TODO_60_63_68_81.refactor_DAG_builder.md
[TODO_73_71_31_84.exec_operation_check_or_info.md]: TODO_73_71_31_84.exec_operation_check_or_info.md
[TODO_89_47_85_02.implement_env_selection.md]: TODO_89_47_85_02.implement_env_selection.md
[TODO_91_75_37_57.implement_shebang_update.md]: TODO_91_75_37_57.implement_shebang_update.md
[TODO_39_94_67_54.rename_client_env_to_global_local.md]: TODO_39_94_67_54.rename_client_env_to_global_local.md
[TODO_20_07_74_69.configure_dirs_at_client_level.md]: TODO_20_07_74_69.configure_dirs_at_client_level.md
[TODO_87_26_62_66.clean_up_venv_driver_args.md]: TODO_87_26_62_66.clean_up_venv_driver_args.md
[TODO_99_29_89_80.warn_only_when_conf_is_required.md]: TODO_99_29_89_80.warn_only_when_conf_is_required.md
[TODO_74_35_76_27.shell_driver_fallback_to_sh.md]: TODO_74_35_76_27.shell_driver_fallback_to_sh.md
[TODO_68_40_26_10.define_env_vars_in_known_env_var_enum.md]: TODO_68_40_26_10.define_env_vars_in_known_env_var_enum.md
[TODO_49_40_51_46.rename_state_names_to_final.md]: TODO_49_40_51_46.rename_state_names_to_final.md
[TODO_65_18_47_30.uv_bootstrap_venv_python_version.md]: TODO_65_18_47_30.uv_bootstrap_venv_python_version.md
[TODO_25_82_21_54.rename_is_app_flag.md]: TODO_25_82_21_54.rename_is_app_flag.md
[TODO_90_53_85_78.proto_dir_path_name.md]: TODO_90_53_85_78.proto_dir_path_name.md
[TODO_56_99_72_68.feature_topic_for_ref_root.md]: TODO_56_99_72_68.feature_topic_for_ref_root.md
[TODO_16_35_39_74.simplify_input_based_default.md]: TODO_16_35_39_74.simplify_input_based_default.md
[TODO_32_41_01_30.review_default_client_conf_file_rel_path.md]: TODO_32_41_01_30.review_default_client_conf_file_rel_path.md
[TODO_79_50_81_23.use_constant_for_dst_dir_name.md]: TODO_79_50_81_23.use_constant_for_dst_dir_name.md
[TODO_80_28_71_21.review_env_clean_up_after_isolated_mode.md]: TODO_80_28_71_21.review_env_clean_up_after_isolated_mode.md
[TODO_05_17_21_85.review_parent_states_list.md]: TODO_05_17_21_85.review_parent_states_list.md
[TODO_43_30_90_54.configure_max_file_log_level.md]: TODO_43_30_90_54.configure_max_file_log_level.md
[TODO_69_28_79_76.skip_exec_argv_args_with_same_value.md]: TODO_69_28_79_76.skip_exec_argv_args_with_same_value.md
[TODO_15_25_41_72.convert_selected_python_to_base_python.md]: TODO_15_25_41_72.convert_selected_python_to_base_python.md
[TODO_71_33_38_11.override_proto_kernel_abs_path_in_conf_getter.md]: TODO_71_33_38_11.override_proto_kernel_abs_path_in_conf_getter.md
