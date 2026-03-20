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
