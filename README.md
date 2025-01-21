# Fetch Website Checker

This is for the fetch interview process, it's designed to import a yaml file and check the uptime of the endpoints listed in the yaml file. I picked python as it should be easier than C or Rust to import dependencies cross-OS, I was wrong.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/leebeck3/fetch-program.git
    ```
2. Navigate to the project directory, on Linux the command would be:
    ```sh
    cd fetch-program
    ```
3. Ensure that python is installed on your system(macOS & Linux):
    ```
    python3 --version
    ```
3. Ensure that python is installed on your system(Windows):
    ```
    python --version
    ```
4. Install the required dependencies(Windows):
    ```sh
    pip install -r minimal-requirements.yaml
    ```
4. Install the required dependencies system-wide(Debian Linux):
    ```sh
    apt install python3-yaml, python3-urllib3
    ```

This list isn't comprehensive, if you have any problems with these instructions please reach out to me at beckerlee3@gmail.com

## Usage

To run the script, use the following command:
```sh
python website-checker.py <input-yaml> (optional)<number-of-threads>
```

## Architecture

The goal of this program is to have everything written out in the main() module as close to human language as possible, enabling easier troubleshooting.


## Next steps

being able to get into the nitty-gritty of why ms > 500ms might be handy eventually depending on how in-depth optimization needs to be. That would turn this into more of a network tool, currently this is built to check lots of sites at a very high-level, so network optimization isn't a concern.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.