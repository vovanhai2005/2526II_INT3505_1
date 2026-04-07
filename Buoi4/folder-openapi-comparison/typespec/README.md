# TypeSpec

## Prerequisites
- [Node.js and npm](https://nodejs.org/) installed on your machine.

## Installation

TypeSpec compiles into standard formats (like OpenAPI) before rendering. First, make sure you have the required TypeSpec dependencies installed locally.

Inside this specific `typespec` directory, run:

```bash
# Initialize a package.json if not present
npm init -y 

# Install the compiler and standard HTTP/OpenAPI libraries
npm install @typespec/compiler @typespec/http @typespec/openapi @typespec/openapi3
```

## Compilation

After installing the compiler, generate the OpenAPI YAML file from your `.tsp` file:

```bash
npx tsp compile main.tsp
```

This generates an OpenAPI 3.0 specification inside a new folder structure: `tsp-output/schema/openapi.yaml`.

## Rendering on Localhost

Now that you have the compiled OpenAPI YAML file, build the HTML documentation using Redocly and serve it locally:

```bash
npx @redocly/cli build-docs tsp-output/schema/openapi.yaml
python3 -m http.server 8080
```

Open `http://127.0.0.1:8080/redoc-static.html` in your web browser to browse your API's documentation!

## Code Generation (Server Stubs & Client SDKs)

Since TypeSpec compiles seamlessly into the standard OpenAPI format, you can easily generate fully functional server stubs and client frontends using the `openapi-generator-cli`.

1. **Compile your TypeSpec** (if you haven't already):
   ```bash
   npx tsp compile main.tsp
   ```

2. **Generate Python Flask Server Code**:
   Use the OpenAPI Generator CLI to generate your boilerplate server. The code will be saved directly in the `generated-server/` directory.
   ```bash
   npx @openapitools/openapi-generator-cli generate -i tsp-output/schema/openapi.yaml -g python-flask -o ./generated-server
   ```

3. **Run your Generated Server**:
   ```bash
   cd generated-server
   pip install -r requirements.txt
   python3 -m openapi_server
   ```
   *Your server will start and the generated endpoints will be active! You can go into the `openapi_server/controllers` folder to write your actual application logic.*
