"""
ptaf2xml.py

This module provides functionality to convert text files to XML. It supports 
both command-line and server modes of operation. 

The module reads input data in PTAF format (Person Telephone Address Family)
and converts it to XML. The PTAF format is a custom format where each
line contains a tag followed by a pipe character and then the content.
"""

# pylint: disable=C0116

import os
import sys
import argparse
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from const import * # pylint: disable=W0401

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

def main() -> None:
    args = get_command_line_arguments()

    if args.serve:
        # Run application as a server
        start_server()
    else:
        # Run application as a command line tool
        run_command_line_tool(args)

def get_command_line_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=CLI_DESCRIPTION)
    parser.add_argument("--prettyprint", dest="pretty", action="store_true", help=CLI_PRETTY)
    parser.add_argument("--no-prettyprint", dest="pretty", action="store_false", help=CLI_NO_PRETTY)
    parser.add_argument("--input", dest="input_file_path", type=str, help=CLI_INPUT_FILE_PATH)
    parser.add_argument("--encoding", dest="encoding", type=str, help=CLI_INPUT_FILE_ENCODING)
    parser.add_argument("--output", dest="output_file_path", type=str, help=CLI_OUTPUT_FILE_PATH)
    parser.add_argument("--serve", action="store_true", help=CLI_SERVE)
    parser.set_defaults(pretty=True)
    parser.set_defaults(encoding=INPUT_FILE_DEFAULT_ENCODING)
    return parser.parse_args()

def start_server() -> None:
    app.run(
        host = os.getenv("HOST", "0.0.0.0").strip(),
        port = int(os.getenv("PORT", "8080").strip()),
    )

def run_command_line_tool(args: argparse.Namespace) -> None:
    if args.input_file_path:
        lines = read_from_file(args.input_file_path, args.encoding)
    elif not sys.stdin.isatty():
        lines = read_from_stdin(args.encoding)
    else:
        print(ERROR_NO_FILE, file=sys.stderr)
        sys.exit(1)

    try:
        xml_tree = convert_to_xml(lines, args.pretty)
    except Exception as e: # pylint: disable=W0718
        print(ERROR_CONVERSION_FAILED, file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)

    xml_str = ET.tostring(xml_tree.getroot(), encoding=OUTPUT_FILE_ENCODING, method="xml")

    if args.output_file_path:
        write_xml_to_file(xml_str, args.output_file_path)
    else:
        print(xml_str)

def convert_to_xml(lines: list[str], prettyprint: bool = True) -> ET.ElementTree:
    root = ET.Element(XML_TAG_PEOPLE)
    current_person = None
    current_family = None

    element_creators = {
        PTAF_TAG_PERSON: create_person_element,
        PTAF_TAG_TELEPHONE: create_telephone_element,
        PTAF_TAG_ADDRESS: create_address_element,
        PTAF_TAG_FAMILY: create_family_element
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(PTAF_SEPARATOR)
        tag = parts[0]
        content = parts[1:]

        if tag not in element_creators:
            raise ValueError(ERROR_INVALID_PTAF_TAG.format(tag))

        element = element_creators[tag](content)
        if tag == PTAF_TAG_PERSON:
            current_person = element
            root.append(current_person)
            current_family = None
        elif tag == PTAF_TAG_FAMILY:
            current_family = element
            if current_person is None:
                raise ValueError(ERROR_INVALID_PTAF_TAG_ORDER)
            current_person.append(current_family)
        else:
            if current_family:
                current_family.append(element)
            elif current_person:
                current_person.append(element)
            else:
                raise ValueError(ERROR_INVALID_PTAF_TAG_ORDER)

    xml_tree = ET.ElementTree(root)

    if prettyprint:
        ET.indent(xml_tree, space=XML_INDENTATION, level=0)

    return xml_tree

def read_from_stdin(encoding: str=INPUT_FILE_DEFAULT_ENCODING) -> list[str]:
    try:
        sys.stdin.reconfigure(encoding=encoding)
        lines = sys.stdin.read().splitlines()
    except Exception as e: # pylint: disable=W0718
        print(ERROR_READ_STDIN, file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)
    return lines

def read_from_file(input_file_path: str, encoding: str=INPUT_FILE_DEFAULT_ENCODING) -> list[str]:
    try:
        with open(input_file_path, "r", encoding=encoding) as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(ERROR_FILE_NOT_FOUND.format(input_file_path), file=sys.stderr)
        sys.exit(1)
    except Exception as e: # pylint: disable=W0718
        print(ERROR_READ_FILE.format(input_file_path), file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)
    return lines

def write_xml_to_file(xml_str: str, output_file_path: str) -> None:
    try:
        with open(output_file_path, "w", encoding=OUTPUT_FILE_ENCODING) as file:
            file.write(xml_str)
    except Exception as e: # pylint: disable=W0718
        print(ERROR_WRITE_FILE.format(output_file_path), file=sys.stderr)
        print(str(e), file=sys.stderr)
        sys.exit(1)

# XML element creation functions:
def create_person_element(content: list[str]) -> ET.Element:
    person = ET.Element(XML_TAG_PERSON)
    if len(content) > 0 and content[0]:
        ET.SubElement(person, XML_TAG_PERSON_FIRSTNAME).text = content[0]
    if len(content) > 1 and content[1]:
        ET.SubElement(person, XML_TAG_PERSON_LASTNAME).text = content[1]
    return person

def create_telephone_element(content: list[str]) -> ET.Element:
    telephone = ET.Element(XML_TAG_TELEPHONE)
    if len(content) > 0 and content[0]:
        ET.SubElement(telephone, XML_TAG_TELEPHONE_MOBILE).text = content[0]
    if len(content) > 1 and content[1]:
        ET.SubElement(telephone, XML_TAG_TELEPHONE_HOME).text = content[1]
    return telephone

def create_address_element(content: list[str]) -> ET.Element:
    address = ET.Element(XML_TAG_ADDRESS)
    if len(content) > 0 and content[0]:
        ET.SubElement(address, XML_TAG_ADDRESS_STREET).text = content[0]
    if len(content) > 1 and content[1]:
        ET.SubElement(address, XML_TAG_ADDRESS_CITY).text = content[1]
    if len(content) > 2 and content[2]:
        ET.SubElement(address, XML_TAG_ADDRESS_ZIPCODE).text = content[2]
    return address

def create_family_element(content: list[str]) -> ET.Element:
    family = ET.Element(XML_TAG_FAMILY)
    if len(content) > 0 and content[0]:
        ET.SubElement(family, XML_TAG_FAMILY_NAME).text = content[0]
    if len(content) > 1 and content[1]:
        ET.SubElement(family, XML_TAG_FAMILY_BORN).text = content[1]
    return family

# API Endpoints:
@app.route("/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        app.logger.error(ERROR_NO_FILE_UPLOADED)
        return jsonify(error=ERROR_NO_FILE_UPLOADED), 400

    file = request.files["file"]
    if file.filename == "":
        app.logger.error(ERROR_NO_FILENAME_SET)
        return jsonify(error=ERROR_NO_FILENAME_SET), 400

    encoding = request.args.get("encoding", INPUT_FILE_DEFAULT_ENCODING)

    try:
        lines = file.read().decode(encoding).splitlines()
    except Exception as e: # pylint: disable=W0718
        app.logger.error(ERROR_READ_UPLOADED_FILE)
        return jsonify({"error": ERROR_READ_UPLOADED_FILE, "message": str(e)}), 400

    prettyprint = request.args.get("prettyprint", "true") == "true"

    try:
        xml_tree = convert_to_xml(lines, prettyprint)
        xml_str = ET.tostring(xml_tree.getroot(), encoding=OUTPUT_FILE_ENCODING, method="xml")
    except Exception as e: # pylint: disable=W0718
        app.logger.error(ERROR_CONVERSION_FAILED)
        app.logger.error(str(e))
        return jsonify({"error": ERROR_CONVERSION_FAILED, "message": str(e)}), 500

    return xml_str, 200, {"Content-Type": "application/xml"}

@app.route("/health")
def health():
    return "OK", 200

@app.route("/version")
def version():
    return os.getenv("VERSION", "unknown"), 200

# Main entry point:
if __name__ == "__main__":
    main()
