# Smart Factory Grids - Autonomous Systems

Welcome to the central GitHub organization for [**Autonomous Systems**](https://www.hs-esslingen.de/en/research/projects/smart-factory-grids-dfg-forschungsimpuls/research-units-and-research-topics/research-unit-2) within the [Smart Factory Grids (SFG) DFG project](https://www.hs-esslingen.de/en/research/projects/smart-factory-grids-dfg-forschungsimpuls).

## Organization Structure

To maintain a clean separation between published research, hardware-specific deployments, and exploratory student work, our codebase is divided across three GitHub organizations:

### 1. [sfg-autonomous-systems](https://github.com/sfg-autonomous-systems)

This is our primary organization for publication-ready research and shared infrastructure. It hosts the official repositories that accompany our published papers, alongside our hardware-agnostic core frameworks, multi-agent coordination tools, and shared deployment pipelines (e.g. [`sfg_agent_common`](https://github.com/sfg-autonomous-systems/sfg_agent_common) or [`sfg_agent_devcontainer`](https://github.com/sfg-autonomous-systems/sfg_agent_devcontainer)).

### 2. [sfg-autonomous-systems-agents](https://github.com/sfg-autonomous-systems-agents)

This organization is strictly for hardware and platform integration. It houses the specialized software stacks, sensor drivers, and deployment configurations specific to our individual agents. In the case of **[SFG-ROS](https://iis-esslingen.github.io/sfg-ros/)**, you will find our reference agent implementations there (e.g. [`sfg_go2`](https://github.com/sfg-autonomous-systems-agents/sfg_go2.git)).

### 3. [sfg-autonomous-systems-sandbox](https://github.com/sfg-autonomous-systems-sandbox)

This space is dedicated to student projects, experimental code, and early-stage research. Successful prototypes from this sandbox are eventually graduated to the main organization once they meet our standards.

## How to Contribute

Please thoroughly review our [Contributing Guidelines](../CONTRIBUTING.md) to understand our development workflows, git submodule policies, and required VS Code tooling before contributing.

*Note for Lab Members: Internal infrastructure documentation is hosted separately [here](https://github.com/sfg-autonomous-systems/sfg_docs).*

## Publications

* **[SFG-ROS:](https://iis-esslingen.github.io/sfg-ros/)** A resource-aware multi-agent software framework designed for dynamic fleet deployments. It utilizes schema-driven traffic routing to isolate high-frequency intra-agent traffic from the global network and bounds network traffic to $\mathcal{O}(1)$ while reducing the per-subscriber CPU scaling penalty by 72.3% versus standard ROS 2. 

## Affiliations

Our research is conducted at the **Institute for Intelligent Systems (IIS)** at the [Esslingen University of Applied Sciences](https://www.hs-esslingen.de/en/).

* [Institute for Intelligent Systems (IIS) Website](https://www.hs-esslingen.de/iis)
* [IIS GitHub Organization](https://github.com/iis-esslingen)

## Funding
Funded by Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) - [Projectnumber 528745080](https://gepris.dfg.de/project/528745080) (FIP 68).
