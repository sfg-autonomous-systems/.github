# Smart Factory Grids - Autonomous Systems

Welcome to the central GitHub organization for [**Autonomous Systems**](https://www.hs-esslingen.de/en/research/projects/smart-factory-grids-dfg-forschungsimpuls/research-units-and-research-topics/research-unit-2) within the [Smart Factory Grids (SFG) DFG project](https://www.hs-esslingen.de/en/research/projects/smart-factory-grids-dfg-forschungsimpuls).

## Organization Structure

All of our code lives in this organization. To keep published research, exploratory student work, and internal lab management cleanly separated, every repository is assigned one of three tiers:

### Stable (`props.tier:stable`)

Publication-ready research, hardware-specific deployments, and shared infrastructure. This includes the official repositories that accompany our published papers, our hardware-agnostic core frameworks, and our reference agent implementations (e.g. [`sfg_agent_common`](https://github.com/sfg-autonomous-systems/sfg_agent_common) or [`sfg_go2`](https://github.com/sfg-autonomous-systems/sfg_go2)), as well as pre-compiled Debian packages for these projects in our [**official APT repository**](https://sfg-autonomous-systems.github.io/sfg_apt_repo/). Changes to the main branches of stable repositories require a reviewed pull request.

### Sandbox (`props.tier:sandbox`)

Student projects, experimental code, and early-stage research. Sandbox repositories are usually private. Successful prototypes are promoted to stable once they meet our standards.

### Restricted (`props.tier:restricted`)

Internal administrative repositories, accessible to administrators only.

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

