<p align="center">
    <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" align="center" width="30%">
</p>
<p align="center"><h1 align="center">OPTIMAL_DCA</h1></p>
<p align="center">
	<em>Empowering Crypto Trades with Optimal Precision</em>
</p>
<p align="center">
	<img src="https://img.shields.io/github/license/cowsking/Optimal_DCA?style=default&logo=opensourceinitiative&logoColor=white&color=0080ff" alt="license">
	<img src="https://img.shields.io/github/last-commit/cowsking/Optimal_DCA?style=default&logo=git&logoColor=white&color=0080ff" alt="last-commit">
	<img src="https://img.shields.io/github/languages/top/cowsking/Optimal_DCA?style=default&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/cowsking/Optimal_DCA?style=default&color=0080ff" alt="repo-language-count">
</p>
<p align="center"><!-- default option, no dependency badges. -->
</p>
<p align="center">
	<!-- default option, no dependency badges. -->
</p>
<br>

##  Table of Contents

- [ Overview](#-overview)
- [ Features](#-features)
- [ Project Structure](#-project-structure)
  - [ Project Index](#-project-index)
- [ Getting Started](#-getting-started)
  - [ Prerequisites](#-prerequisites)
  - [ Installation](#-installation)
  - [ Usage](#-usage)
  - [ Testing](#-testing)
- [ Project Roadmap](#-project-roadmap)
- [ Contributing](#-contributing)
- [ License](#-license)
- [ Acknowledgments](#-acknowledgments)

---

##  Overview

OptimalDCA is an innovative open-source project designed to automate and optimize cryptocurrency transactions on the Coinbase Pro platform. It simplifies the process of depositing funds, buying cryptocurrencies based on market cap weights, and withdrawing to specified addresses. With features like automated dependency updates and secure JWT generation, it offers a reliable, efficient solution for tech-savvy investors seeking to streamline their cryptocurrency trading activities.

---

##  Features

|      | Feature         | Summary       |
| :--- | :---:           | :---          |
| ⚙️  | **Architecture**  | <ul><li>Uses Docker for containerization, ensuring consistent environments across different platforms. See [`Dockerfile`](https://github.com/brndnmtthws/optimal-buy-cbpro/blob/main/Dockerfile).</li><li>Utilizes `systemd` for managing the application's lifecycle. See [`systemd`](https://github.com/brndnmtthws/optimal-buy-cbpro/tree/main/systemd) directory.</li><li>Employs a modular approach with separate scripts for different functionalities. See [`coinbase_trade`](https://github.com/brndnmtthws/optimal-buy-cbpro/tree/main/coinbase_trade) directory.</li></ul> |
| 🔩 | **Code Quality**  | <ul><li>Code is well-structured and follows Python best practices.</li><li>Uses `pytest` and `pytest-mock` for unit testing, ensuring code reliability. See [`requirements-test.txt`](https://github.com/brndnmtthws/optimal-buy-cbpro/blob/main/requirements-test.txt).</li><li>Dependabot is used for automated dependency updates, ensuring code stays current and secure. See [`.github/dependabot.yml`](https://github.com/brndnmtthws/optimal-buy-cbpro/blob/main/.github/dependabot.yml).</li></ul> |
| 📄 | **Documentation** | <ul><li>Primary language used is Python. See [`primary_language`](https://github.com/brndnmtthws/optimal-buy-cbpro).</li><li>Includes a `Dockerfile` for containerization. See [`containers`](https://github.com/brndnmtthws/optimal-buy-cbpro).</li><li>Provides installation and usage commands for Docker. See [`install_commands`](https://github.com/brndnmtthws/optimal-buy-cbpro) and [`usage_commands`](https://github.com/brndnmtthws/optimal-buy-cbpro).</li></ul> |
| 🔌 | **Integrations**  | <ul><li>Integrates with the Coinbase Pro API for cryptocurrency transactions. See [`coinbase_trade`](https://github.com/brndnmtthws/optimal-buy-cbpro/tree/main/coinbase_trade) directory.</li><li>Uses SQLAlchemy for database management. See [`optimal_buy_cbpro/history.py`](https://github.com/brndnmtthws/optimal-buy-cbpro/blob/main/optimal_buy_cbpro/history.py).</li></ul> |

---

##  Project Structure

```sh
└── Optimal_DCA/
    ├── .github
    │   ├── FUNDING.yml
    │   └── dependabot.yml
    ├── Dockerfile
    ├── LICENSE
    ├── MANIFEST.in
    ├── README.md
    ├── buy-the-dip.gif
    ├── coinbase_trade
    │   ├── another.py
    │   ├── commit_deposit.py
    │   ├── deposit.py
    │   ├── deposit_try.py
    │   ├── generate_JWT.py
    │   ├── test.py
    │   ├── test2.py
    │   └── test_all.py
    ├── crypto.gif
    ├── optimal_buy_cbpro
    │   ├── __init__.py
    │   ├── history.py
    │   └── optimal_buy_cbpro.py
    ├── requirements-test.txt
    ├── setup.py
    ├── systemd
    │   ├── optimal-buy-cbpro-buy.service
    │   ├── optimal-buy-cbpro-buy.timer
    │   ├── optimal-buy-cbpro-deposit.service
    │   └── optimal-buy-cbpro-deposit.timer
    └── tests
        ├── __init__.py
        ├── test_optimal_buy_cbpro.py
        └── test_real_trading.py
```


###  Project Index
<details open>
	<summary><b><code>OPTIMAL_DCA/</code></b></summary>
	<details> <!-- __root__ Submodule -->
		<summary><b>__root__</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/MANIFEST.in'>MANIFEST.in</a></b></td>
				<td>- MANIFEST.in serves as a directive for packaging additional files in the project distribution<br>- It ensures the inclusion of README.md and LICENSE files, as well as recursively incorporating all Python files from the tests directory<br>- This contributes to the comprehensive packaging and distribution of the project.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/requirements-test.txt'>requirements-test.txt</a></b></td>
				<td>- Requirements-test.txt outlines the necessary dependencies for testing the project<br>- It includes libraries for unit testing (pytest, pytest-mock), interacting with the Coinbase API (coinbase-advanced-py), database management (SQLAlchemy), and environment variable handling (python-dotenv).</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/setup.py'>setup.py</a></b></td>
				<td>- Setup.py serves as the installation guide for the 'optimal_buy_cbpro' project<br>- It outlines the necessary dependencies, testing requirements, and entry points for the application<br>- Additionally, it provides metadata about the project, such as the author, version, and description<br>- This file is crucial for setting up the project environment correctly.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/Dockerfile'>Dockerfile</a></b></td>
				<td>- The Dockerfile establishes a Python 3 environment, sets the working directory to /appsrc, and copies the application source code into it<br>- It then installs the application dependencies and removes the source code to keep the Docker image clean<br>- The entry point is set to initiate the 'optimal-buy-cbpro' command upon container startup.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- .github Submodule -->
		<summary><b>.github</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/.github/FUNDING.yml'>FUNDING.yml</a></b></td>
				<td>- FUNDING.yml, located in the .github directory, establishes a funding model for the project<br>- It designates 'brndnmtthws' as the recipient of any financial contributions made through GitHub<br>- This mechanism supports the ongoing development and maintenance of the open-source project.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/.github/dependabot.yml'>dependabot.yml</a></b></td>
				<td>- Dependabot.yml, located in the .github directory, manages automated dependency updates for the project<br>- It's configured to check for Python package updates daily at 10:00 and can open up to 10 pull requests simultaneously<br>- Identified updates are reviewed and assigned to user brndnmtthws, ensuring the project's dependencies remain current and secure.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- coinbase_trade Submodule -->
		<summary><b>coinbase_trade</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/another.py'>another.py</a></b></td>
				<td>- Leveraging the Coinbase API, another.py generates a JSON Web Token (JWT) for secure communication with the brokerage accounts endpoint<br>- It uses the JWT generator from the Coinbase library, along with a specified API key and secret, to create and print the JWT token.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/commit_deposit.py'>commit_deposit.py</a></b></td>
				<td>- Commit_deposit.py in the coinbase_trade module facilitates the commitment of deposits on the Coinbase platform<br>- It generates a JSON Web Token (JWT) for secure authorization and sends a POST request to the Coinbase API<br>- The response, containing the deposit transaction details, is then returned in JSON format.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/test2.py'>test2.py</a></b></td>
				<td>- Coinbase_trade/test2.py is a script that interacts with the Coinbase and CoinGecko APIs to fetch cryptocurrency data<br>- It retrieves market cap information, calculates coin weights, and fetches product and price details for Bitcoin, Ethereum, and Litecoin<br>- The script also handles exceptions and prints relevant information for debugging purposes.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/generate_JWT.py'>generate_JWT.py</a></b></td>
				<td>- Generate_JWT.py in the coinbase_trade directory is responsible for creating a JSON Web Token (JWT) using the Coinbase API<br>- It uses the API key and secret to authenticate and make a GET request to the Coinbase API, returning the user's brokerage account details.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/test.py'>test.py</a></b></td>
				<td>- The 'coinbase_trade/test.py' script primarily facilitates interaction with the Coinbase API<br>- It establishes a client connection using API credentials, retrieves account balances, and lists payment methods<br>- The script also contains commented-out code for listing trades, placing a market order, and fetching product details, indicating potential future functionalities.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/test_all.py'>test_all.py</a></b></td>
				<td>- The code in 'coinbase_trade/test_all.py' is a script for automating cryptocurrency trading on Coinbase Pro<br>- It supports two modes: 'deposit' and 'buy'<br>- In 'deposit' mode, it deposits a specified amount of fiat currency into the user's account<br>- In 'buy' mode, it calculates the weights of different cryptocurrencies based on their market caps, and places buy orders accordingly<br>- It also supports withdrawal of cryptocurrencies to specified addresses.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/deposit_try.py'>deposit_try.py</a></b></td>
				<td>- The 'deposit_try.py' in the 'coinbase_trade' directory is primarily responsible for depositing funds into a Coinbase account<br>- It retrieves a JWT token for authentication, constructs a request with the deposit details, and sends it to the Coinbase API<br>- The response from this operation is then printed out.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/coinbase_trade/deposit.py'>deposit.py</a></b></td>
				<td>- Depositing funds into a Coinbase account is the primary function of the 'deposit.py' script within the 'coinbase_trade' directory<br>- It constructs a JSON Web Token (JWT) for secure authorization, then sends a POST request to the Coinbase API to deposit a specified amount<br>- The script leverages environment variables for sensitive data like API keys.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- systemd Submodule -->
		<summary><b>systemd</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/systemd/optimal-buy-cbpro-deposit.service'>optimal-buy-cbpro-deposit.service</a></b></td>
				<td>- The systemd service file, optimal-buy-cbpro-deposit.service, manages the deployment and operation of the Docker container for the optimal-buy-cbpro application<br>- It ensures the application is properly initialized after the Docker service, handles updates, and sets the application's running parameters<br>- This contributes to the overall project by automating the application's lifecycle management.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/systemd/optimal-buy-cbpro-deposit.timer'>optimal-buy-cbpro-deposit.timer</a></b></td>
				<td>- The 'optimal-buy-cbpro-deposit.timer' within the systemd directory sets a schedule for a Coinbase Pro deposit operation<br>- It triggers the associated service every Monday at midnight<br>- This routine deposit operation is a crucial part of the overall project's financial management system, ensuring regular funding for optimal cryptocurrency purchases.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/systemd/optimal-buy-cbpro-buy.service'>optimal-buy-cbpro-buy.service</a></b></td>
				<td>- The systemd service file, optimal-buy-cbpro-buy.service, manages the execution of the optimal-buy-cbpro Docker container<br>- It ensures the container is run after the Docker service, pulling the latest version, and setting up necessary parameters for operation<br>- It's integral to the project's architecture, enabling automated cryptocurrency purchases via the Coinbase Pro API.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/systemd/optimal-buy-cbpro-buy.timer'>optimal-buy-cbpro-buy.timer</a></b></td>
				<td>- The 'optimal-buy-cbpro-buy.timer' within the systemd directory schedules the execution of the 'optimal-buy-cbpro-buy.service'<br>- It triggers a Coinbase Pro buy order daily at 00:28<br>- This timer is integral to the project's architecture, ensuring regular cryptocurrency purchases and contributing to the overall investment strategy.</td>
			</tr>
			</table>
		</blockquote>
	</details>
	<details> <!-- optimal_buy_cbpro Submodule -->
		<summary><b>optimal_buy_cbpro</b></summary>
		<blockquote>
			<table>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/optimal_buy_cbpro/optimal_buy_cbpro.py'>optimal_buy_cbpro.py</a></b></td>
				<td>- The provided Python file, `optimal_buy_cbpro.py`, is part of a larger project that interacts with the Coinbase Pro API to manage cryptocurrency transactions<br>- The main purpose of this file is to facilitate optimal buying operations for different cryptocurrencies like Bitcoin (BTC), Ethereum (ETH), and JASMY<br>- The code achieves this by using the RESTClient from the Coinbase API to send requests and receive responses<br>- It also uses the SQLAlchemy models defined in the `history.py` file to manage Order, Deposit, and Withdrawal operations<br>- The file also handles precision differences between various cryptocurrencies and their prices, ensuring accurate calculations and transactions<br>- It defines specific decimal precision for different coins and their prices, and provides a default precision for other cases<br>- In summary, this file is a crucial component of the project that enables precise and efficient cryptocurrency buying operations on Coinbase Pro.</td>
			</tr>
			<tr>
				<td><b><a href='https://github.com/cowsking/Optimal_DCA/blob/master/optimal_buy_cbpro/history.py'>history.py</a></b></td>
				<td>- "History.py" in the "optimal_buy_cbpro" project defines the structure of the "orders", "withdrawals", and "deposits" tables in the database<br>- It also includes a function to establish a session with the database<br>- This file is crucial for managing transactions and maintaining the financial history within the project.</td>
			</tr>
			</table>
		</blockquote>
	</details>
</details>

---
##  Getting Started

###  Prerequisites

Before getting started with Optimal_DCA, ensure your runtime environment meets the following requirements:

- **Programming Language:** Python
- **Container Runtime:** Docker


###  Installation

Install Optimal_DCA using one of the following methods:

**Build from source:**

1. Clone the Optimal_DCA repository:
```sh
❯ git clone https://github.com/cowsking/Optimal_DCA
```

2. Navigate to the project directory:
```sh
❯ cd Optimal_DCA
```

3. Install the project dependencies:


**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker build -t cowsking/Optimal_DCA .
```




###  Usage
Run Optimal_DCA using the following command:
**Using `docker`** &nbsp; [<img align="center" src="https://img.shields.io/badge/Docker-2CA5E0.svg?style={badge_style}&logo=docker&logoColor=white" />](https://www.docker.com/)

```sh
❯ docker run -it {image_name}
```


###  Testing
Run the test suite using the following command:
echo 'INSERT-TEST-COMMAND-HERE'

---
##  Project Roadmap

- [X] **`Task 1`**: <strike>Implement feature one.</strike>
- [ ] **`Task 2`**: Implement feature two.
- [ ] **`Task 3`**: Implement feature three.

---

##  Contributing

- **💬 [Join the Discussions](https://github.com/cowsking/Optimal_DCA/discussions)**: Share your insights, provide feedback, or ask questions.
- **🐛 [Report Issues](https://github.com/cowsking/Optimal_DCA/issues)**: Submit bugs found or log feature requests for the `Optimal_DCA` project.
- **💡 [Submit Pull Requests](https://github.com/cowsking/Optimal_DCA/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/cowsking/Optimal_DCA
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="left">
   <a href="https://github.com{/cowsking/Optimal_DCA/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=cowsking/Optimal_DCA">
   </a>
</p>
</details>

---

##  License

This project is protected under the [SELECT-A-LICENSE](https://choosealicense.com/licenses) License. For more details, refer to the [LICENSE](https://choosealicense.com/licenses/) file.

---

##  Acknowledgments

- List any resources, contributors, inspiration, etc. here.

---
