# PTAF to XML Converter

This application converts a text file in PTAF (Plain Text Address Format) to XML. The script reads the input file, processes the data, and returns the resulting XML. It is a Python script that can be run natively or in a Docker container.

## Running the application in a Docker container (recommended)

### Prerequisites

- Docker
- docker-compose (optional but recommended)
- cURL (optional)

### Building and starting the application using docker-compose (recommended)

```sh
docker-compose up -d --build
```

The `--build` parameter can be skipped in subsequent deployments without code changes.

Text files in PTAF format can now be POSTed to the Docker container on port `8080` to the path `/convert`:

```sh
curl -F 'file=@test_input.txt' http://localhost:8080/convert
curl -F 'file=@test_input.txt' http://localhost:8080/convert?prettyprint=false
```

If you prefer to use a graphical user interface, use a tool like Postman or visit `http://localhost:8081` in a web browser after starting the Swagger UI like this:

```sh
docker run -p 8081:8080 -e SWAGGER_JSON=/foo/openAPI.yaml -v $(pwd)/openAPI.yaml:/foo/openAPI.yaml swaggerapi/swagger-ui
```

### Building and starting the application without docker-compose

As an alternative to docker-compose, the container can be built and started like this:

```sh
docker build -t ptaf2xml .
docker run -p 8080:8080 ptaf2xml
```

## Running the application locally on your system

During development it may sometimes be convenient to run the application locally.

### Prerequisites

- Python 3.9 or later
- pip
- flask

### Installing the required tools

This depends on your system, but in Debian/Ubuntu it would look something like this:

```sh
sudo apt install python3.9
sudo apt install python3.9-distutils
pip install -r requirements.txt
```

You can run the script from the command line. You can specify a file path or read from standard input.

### Arguments

- `-h` (optional): Show help message and exit.
- `--input FILE_PATH` (optional): The path to the input text file. If not provided, the script reads from standard input.
- `--encoding ENCODING` (optional): Set the text encoding of the input text file. The default is utf-8.
- `--output FILE_PATH` (optional): The path to the output XML file. If not provided, the script writes to standard output.
- `--prettyprint` (optional): Add line breaks and indentation to the XML output. This is the default behaviour.
- `--no-prettyprint` (optional): Return the XML file without line breaks and indentations.
- `--serve` (optional): Start the application in server mode. This is how the application should be started in Docker containers.


### Examples

```sh
python ptaf2xml.py --input test_input.txt
python ptaf2xml.py --input test_input.txt --no-prettyprint
python ptaf2xml.py --input test_input.txt --output test_output.xml
cat test_input.txt | python ptaf2xml.py > test_output.xml
```

## Input File Format

The input file should be in PTAF format, where each line represents a different type of data:

- `P|firstname|lastname`: Person's first and last name.
- `T|mobile|home`: Telephone numbers (mobile and home).
- `A|street|city|zipcode`: Address details.
- `F|name|born`: Family member's name and birth year.

### Example Input File

```
P|John|Doe
T|123456|234567
A|123 Main St|Anytown|12345
F|Jane Doe|1990
T|987654
```

If the text encoding of the input file is anyting other than `utf-8` this must be specified with the `encoding` parameter.

## Output

The application returns an XML representation of the input data. An XML schema is available in the file `people.xsd`.

### Example Output

```xml
<people>
    <person>
        <firstname>John</firstname>
        <lastname>Doe</lastname>
        <phone>
            <mobile>123456</mobile>
            <home>234567</home>
        </phone>
        <address>
            <street>123 Main St</street>
            <city>Anytown</city>
            <zipcode>12345</zipcode>
        </address>
        <family>
            <name>Jane Doe</name>
            <born>1990</born>
            <phone>
                <mobile>987654</mobile>
            </phone>
        </family>
    </person>
</people>
```

## Development

After making changes to the source code, increase the version number in the .env file and build a new Docker image like this:

```sh
docker-compose build --no-cache
```
