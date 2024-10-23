# Weather Data Scraper and Analyzer

## Introduction
Welcome to the Weather Data Scraper and Analyzer project! This initiative aims to provide valuable insights into historical weather patterns in Timisoara, Romania, to assist **fictional** local government entities in making informed decisions regarding outdoor activities and event planning.

By leveraging data from a reliable weather API, our project collects and analyzes historical weather data to identify trends and patterns that can inform decisions on optimal days for outdoor events. Through statistical analysis and visualizations, we aim to deliver actionable insights that will help local authorities better understand and respond to the community's needs regarding outdoor programming.

## Features
- Fetches historical weather data using a weather API ([Open-Meteo](https://open-meteo.com/en/docs/historical-weather-api)).
- Stores collected weather data in a structured format for easy access and analysis.
- Analyzes weather data to calculate key trends such as average temperatures and rainfall frequency, humidity, wind, etc.
- Visualizes data trends through interactive charts and graphs for clear and effective communication of findings.

## Technologies Used
- **Languages**: Python, bash
- **Data Storage**: SQLite - A lightweight, file-based database suitable for structured storage and queries.
- **Visualization Libraries**: 
  - Matplotlib: For generating static graphs and visualizations.
  - Seaborn: For enhanced statistical graphics and visualizations.
- **Weather API**: WeatherStack for accessing historical weather data.
- **Containerization**: Docker (python 3.12-slim base image) to ensure consistent development and deployment environments.
- **Windows Subsystem for Linux (WSL)**: For creating a Unix-like environment on Windows machines to ensure compatibility with Unix-based tools and Docker containers.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Project Setup Instructions

## Prerequisites
Before you begin, ensure you have the following installed on your machine:
- **Docker Desktop**: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Windows Subsystem for Linux (WSL)** - _Skip if not installed already or if you're using MacOS_: [Install WSL](https://docs.microsoft.com/en-us/windows/wsl/install) 
- **Python**: While Docker provides Python in the container, having Python installed locally can be useful for testing or running scripts outside of Docker.
- **IDE**: VSCode code editor of your choice (e.g., DataSpell, PyCharm, etc).

## Step 0: Set up the Ubuntu environment (SKIP if you're using MacOS):
- Open your terminal (Powershell or cmd)
- See what options are available: `wsl --list --online`
- install Ubuntu: `wsl --install -d Ubuntu`
  - it will require you to enter a new username for UNIX and a password
- after doing that, check if Ubuntu is installed: `wsl --list --verbose`
- Set Ubuntu to be the default distribution: `wsl --setdefault Ubuntu`
- Check again if it's the default (*): `wsl --list --verbose`
- switch to Ubuntu: `wsl -d Ubuntu` from the cmd/powershell **or you can access the WSL terminal (search on your PC `WSL` and enter**
- update the env `sudo apt update` and `sudo apt upgrade -y`
  ### Step 0.1: Set up GIT auth credentials inside the Ubuntu environment:

  - Set up new SSH in WSL `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
    - When prompted to enter a file in which to save the key **press enter** to accept the default location
    - When prompted to add a passphrase, **press enter again** to skip the passphrase
  - Add the SSH key to the SSH agent:
    ```bash
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa
    ```
  - Add the SSH key to Github:
    - Access the folder manually with path: `\\wsl.localhost\Ubuntu\home\YourUserYouCreatedWSL\.ssh`
    ![image](https://github.com/user-attachments/assets/f7ea887b-d6ac-44b8-8333-7b5bd071475f)
    - open id_rsa.pub and copy its content
  - Go to Github -> Settings -> SSH and GPG keys -> New SSH key
    - paste it, save it
  - Now let's check the SSH connection `ssh -T git@github.com`
    You should see a message like this:
    ![image](https://github.com/user-attachments/assets/8f85ad9e-e847-45e5-923a-1cffe8e7ab37)

## Step 1: Clone the Repository
In the WSL terminal run the following command to clone the project repository:

`git clone https://github.com/l1uzz3/weather-scraper-analyzer.git`
## Step 2: Navigate to the project directory
`cd weather-scraper-analyzer`
## Step 3: Build the Docker image:
**_OPEN DOCKER DESKTOP_- login to your account, bla bla**

**Here we have two options depending on what IDE you're going to use:**
   **1. VScode IDE:**
  -  **you only have to build the image once.** Then we could work together.
     **Make sure to be in the repo directory `cd`**
     **Open the project in VScode using `code .`**
      - A prompt will appear in the bottom-right corner of VSCode asking if you want to "Reopen in Container." Click Reopen in Container. This will automatically build and start the Docker container if it's not already built. 
   - **Rebuilding images should only be necessary when the Dockerfile or other configuration files are modified!**
     #### Now you're inside the Docker container and you can work on the project.
     
  **2. Any other IDE**
  Since other IDEs don't really have an extension like VScode's Remote Containers, we have to do this manually on the terminal.
  - In the WSL terminal run `docker build -t weather-scraper-analyzer .`
  - Create, run and mount the new container: `docker run -it -v /home/YourWSLusernameCreated/weather-scraper-analyzer:/home/weather_project_user/workspace --name weather-container weather-scraper-analyzer /bin/bash` **replace `YourWSLusernameCreated`** with the WSL username.
  **What we did with the last command was to create, run and MOUNT(create relationship between Docker container and the project directory)** the directory. Now everything you will edit inside your project directory `/home/YourWSLusernameCreated/weather-scraper-analyzer` will be seen (stored) in `/home/weather_project_user/workspace` ==> **INSIDE THE DOCKER CONTAINER.**
  - check the container created by running in the terminal `docker ps`. You should see it there.
    ![image](https://github.com/user-attachments/assets/ee2a0b05-ee8e-4478-8cde-ab50c0db383c)
  **Now you can navigate to your working directory and open it in the IDE you're using: in my case Dataspell**
    ![image](https://github.com/user-attachments/assets/0182c1f9-21c0-4355-9473-156c098b4d00)
##### After editing files inside the docker container, just save them. 
**When you finished working make sure to save the files than write in the terminal `docker stop weather-container`**. 

## Docker workflow:
When you want to reload the work:
- Open Docker Desktop
- in the WSL terminal run `docker start weather-container` (check if it started with `docker ps` or on Docker Desktop)
To work INSIDE the docker you have to access it after you started it:
- Run `docker exec -it weather-container /bin/bash`
Now you can sucessfully work inside the container by opening the WSL path to the project directory again.
- When you're finished `docker stop weather-container`
## Other suggestions
**Make sure you create another branch (with the related issue name) when you're working on issues**
**After you edit a file make sure to `git add` it, `git commit -m "message"` it, and `git push origin master`**
**When you reload the work on the project, make sure that you are up-to-date with the git repo: using `git pull`**

# Why these technologies?

This project uses **WSL (Windows Subsystem for Linux)**, **Docker**, and a **Python 3.12-slim base image** to create an efficient, cross-platform development environment. Here’s how each of these technologies contributes to the workflow:

### 1. WSL (Windows Subsystem for Linux)
WSL allows users on Windows to run a native Linux environment without the need for a virtual machine. By providing a Unix-like environment, WSL ensures compatibility with Linux-based tools and scripts, which are essential for most modern development workflows.

- **Seamless compatibility**: Since most production environments are Linux-based, WSL ensures the development environment mirrors production while still allowing Windows users to stay on their preferred operating system.
- **Efficient Tool Usage**: Many data science and web development tools, like Docker, run more smoothly on Linux. WSL provides direct access to these tools without needing dual-boot setups or additional hardware.
- **Collaboration Across Platforms**: By using WSL, Windows users can collaborate seamlessly with teammates using Linux or Mac, ensuring platform compatibility across the board.

### 2. Docker
Docker containers are used to isolate and encapsulate the project environment, ensuring consistency across different systems. Each container runs its own isolated instance of the Python environment, including dependencies and configurations.

- **Consistency across machines**: Docker ensures that all users work with the same environment, independent of their operating system. This eliminates the issue of platform-specific bugs or inconsistencies.
- **Portability**: The project, along with all its dependencies, can easily be packaged into a container and deployed on any machine or server. This is essential for portability and scalability, especially for future deployment.
- **Environment isolation**: Docker keeps the Python environment isolated from the host system, preventing conflicts between different versions of dependencies or tools.
- **Reproducible environment**: The Docker container includes everything needed to run the project, meaning that anyone can clone the repository, build the container, and have the project up and running without additional setup.

### 3. Python 3.12-slim base image
The Python 3.12-slim image is a lightweight, minimal base image that includes only the essentials for running Python. This image is highly customizable, allowing users to add only the libraries required for the project.

- **Efficiency**: Using the slim version of Python ensures that the container remains lightweight and fast. This reduces build times and minimizes resource usage.
- **Customizable**: Since the slim image contains only the bare essentials, it allows for complete control over which packages and dependencies are installed, optimizing performance for the specific needs of the project.
- **Latest Python features**: The Python 3.12 version ensures access to the latest language features, improvements, and security patches.
- **Security**: A slim image limits unnecessary packages, reducing the potential attack surface and making the environment more secure.

### How these technologies work together
The combination of WSL, Docker, and the Python 3.12-slim base image creates a unified, efficient, and reproducible environment. This setup ensures that:
- Developers using Windows, Mac, or Linux can collaborate seamlessly, thanks to Docker’s cross-platform capabilities (since we have a MacOS colleague as well).
- The development environment remains consistent across all machines, eliminating platform-specific issues.
- The lightweight Python image reduces overhead and improves performance, allowing for faster builds and deployment.

By leveraging these technologies, the project benefits from an optimized development process, enhanced portability, and seamless collaboration across different platforms.


    
    
    
