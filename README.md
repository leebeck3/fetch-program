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
4. Install the required dependencies system-wide(Debian):
    ```sh
    apt install python3-yaml, python3-urllib3
    ```
Note: on different OS's there might be different packages, I can test linux or windows, don't have a way to currently virtualize macOS.  

## Usage

To run the script, use the following command:
```sh
python website-checker.py <input-yaml> (optional)<number-of-threads>
```

note: if number of workers isn't set it defaults to 5


## Architecture

The goal of this program is to have everything written out in the main() module as close to human language as possible, enabling easier troubleshooting.


## Next steps

being able to get into the nitty-gritty of why ms > 500ms might be handy eventually depending on how in-depth optimization needs to be. That would turn this into more of a network tool, currently this is built to check lots of sites at a very high-level, so network optimization isn't a concern.

If I needed to really get down to the details for this, I'd rewrite this in C or Rust for performance sake.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.