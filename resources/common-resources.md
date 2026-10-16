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
