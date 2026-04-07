const wp = require('webapi-parser').WebApiParser;
const path = require('path');
const fs = require('fs');

async function main() {
  await wp.init();
  const filePath = 'file://' + path.resolve(__dirname, 'api.raml');
  const model = await wp.raml10.parse(filePath);
  const oas3 = await wp.oas30.generateString(model);
  console.log(oas3);
}
main().catch(console.error);
