<p align="center">
    <a href="https://github.com/TechlauncherFireApp/mobile" rel="noopener">
        <img width=300px src="https://raw.githubusercontent.com/TechlauncherFireApp/mobile/main/assets/logo_gradient.png" ></img>
    </a>
    <p align="center">
        A web API designed to efficiently manage and schedule volunteer firefighters.
    </p>
</p>

<div align="center">

[![Build](https://github.com/TechlauncherFireApp/backend/actions/workflows/deploy.yaml/badge.svg)](https://github.com/TechlauncherFireApp/backend/actions/workflows/deploy.yaml)
[![Test](https://github.com/TechlauncherFireApp/backend/actions/workflows/test.yml/badge.svg)](https://github.com/TechlauncherFireApp/backend/actions/workflows/test.yml)

</div>

### Backend Setup

The following steps describe the _operations_ required to get the backend environment setup and working on a system.
The specific steps for _your_ system will vary and are therefore not detailed beyond linking to the individual install
instructions. If  you require help getting started, please post in the discord #general.

Please note that the versions used here are quite specific, please follow them. 

Its recommended you use [PyCharm Ultimate](https://www.jetbrains.com/pycharm/download/), you get it for free with you
`anu.edu.au` email address. 

1. **Install Python 3.8+**: [Steps](https://www.python.org/downloads/)
2. **Run** the following commands in a terminal:\
    a. `pip install pipenv`\
    b. `pipenv install`
3. **Install Minizinc**:  [Steps](https://www.minizinc.org/software.html)
4. **Install the AWS CLI**: [Steps](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
5. **Configure the AWS CLI**: [Steps](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html#cli-configure-quickstart-config)\
    **Note:** Use the `AWS_ACCESS_KEY` and `AWS_SECRET_ACCESS_KEY` provided to you when you joined the team. 
6. **Restart** your IDE so as to update your path. 
7. **Create** a run configuration by adding a `Flask` runtime using the settings:\
    _Target Type:_ `Script Path`\
    _Target:_ `find application.py in root directory`\
    _FLASK_ENV:_ `development`\
    _FLASK_DEBUG:_ `true`\
    _Add Contents Root to Python Path:_ `true`\
    _Add Source Root to Python Path:_ `true` 
