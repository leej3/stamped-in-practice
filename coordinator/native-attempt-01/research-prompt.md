# Potential gains and brain activity

Does increasing potential monetary gain produce a greater fMRI response in the ventromedial prefrontal cortex (vmPFC) in the NARPS equal-indifference group?

Test the hypothesis that this response increases with potential gain.
Participants performed a mixed-gambles task, deciding whether to accept gambles with possible gains and losses.
In this group, the range of potential gains was twice the range of potential losses.

Investigate the question at the group-analysis stage using the supplied 54 participant gain-effect maps and metadata.
Preprocessing and individual modeling are fixed inputs, described in `upstream-methods.md`; do not repeat them or download time-series scans.
Choose scientifically defensible group models, quality checks, software and visualizations.
Account for what the supplied effect estimates measure and the limits of their upstream model.
Use whole-brain correction for multiple comparisons when evaluating support for the hypothesis, as required by the original study; justify how you identify vmPFC.

Produce a concise scientific report with informative figures and the code and results supporting your conclusions.
Explain uncertainty, exclusions and limitations, including what a lack of support would mean.
Prior teams' answers are not ground truth or a required result.

Source: [NARPS original analysis instructions, Hypothesis 1](https://www.narps.info/files/narps_instructions_for_analysis_teams.pdf).

Common resources

# Available resources

The supplied scientific files are under `input/` in your current workspace.
Choose scientifically suitable methods, tools and file organization.

A prepared Python 3.13.16 interpreter is available at `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/.pixi/envs/default/bin/python`.
It includes NumPy 2.5.4, SciPy 1.18.1, pandas 3.0.6, Matplotlib 3.11.2, NiBabel 5.4.2 and Nilearn 0.14.1.
The optional environment manifest is `/Users/johnlee/.local/state/stamped-in-practice/narps-neutral-v1/common-environment/pixi.toml`.
The environment was prepared as a common resource; you may use it or select other suitable software.

The same shell, Git, Pixi, Python package installation and native web/reference tools are available to every worker.
Network access is enabled; an individual website or service may be unavailable.
Keep task-specific installations and changes in your workspace and leave shared software and configuration unchanged.

Three sessions share this host, which has ten CPU cores and 32 GiB of memory.
There is no separate CPU, memory or elapsed-time quota per session.
Common numerical thread environment variables default to one thread; this is a starting setting, not a required analysis method.
Coordinator execution logging and preservation occur outside your delivery and do not require a particular workflow.


Choose the tools, analysis methods and delivery organization appropriate to the scientific task.
Keep task-specific installations and changes within your workspace, leaving shared configuration unchanged.
When finished, identify the report, code and supporting results in your final response and state any remaining limitations.
