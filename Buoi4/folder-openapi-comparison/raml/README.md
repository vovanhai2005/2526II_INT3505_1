# RAML (RESTful API Modeling Language)

## Prerequisites
- [Node.js and npm](https://nodejs.org/) installed on your machine.
- Python 3 installed.

## Installation Tools

We will use a popular tool called `raml2html` to generate an HTML documentation page.

Install the required package globally in your terminal:

```bash
npm install -g raml2html
```

## Generating & Rendering on Localhost

1. Inside this directory, use the following command to convert the RAML file into a static `.html` webpage:

```bash
raml2html api.raml > index.html
```

2. Start a local server with Python to view the output:

```bash
python3 -m http.server 3000
```

3. Open `http://localhost:3000` in your web browser. Because the file is named `index.html`, the browser will automatically render your RAML documentation.

## Code Generation (Server Stubs & Client SDKs)

Since most modern code generators require the OpenAPI format natively, we first convert the `api.raml` file into an OpenAPI 3.0 specification (`openapi.yaml`), and then we run the `openapi-generator-cli`.

1. **Install MuleSoft's webapi-parser**:
   ```bash
   npm install webapi-parser
   ```

2. **Convert RAML to OpenAPI**:
   *(A `convert.js` utility script has been provided in this directory).*
   ```bash
   node convert.js > openapi.yaml
   ```

3. **Clean up AMF Extension formats**:
   *(A `fix.js` script removes MuleSoft specific extensions to ensure strict standard OpenAPI validation).*
   ```bash
   node fix.js
   ```

4. **Generate Python Flask Server Code**:
   Use the OpenAPI Generator CLI to generate your boilerplate server. The code will be saved in the `generated-server/` directory.
   ```bash
   npx @openapitools/openapi-generator-cli generate -i openapi.yaml -g python-flask -o ./generated-server
   ```
