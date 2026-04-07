const fs = require('fs');
let data = JSON.parse(fs.readFileSync('openapi.yaml', 'utf8'));

function fix(obj) {
  if (Array.isArray(obj)) {
    obj.forEach(fix);
  } else if (typeof obj === 'object' && obj !== null) {
    if (obj['x-amf-merge'] && obj['x-amf-merge'].length > 0) {
      Object.assign(obj, obj['x-amf-merge'][0]);
      delete obj['x-amf-merge'];
    }
    for (let key in obj) {
      fix(obj[key]);
    }
  }
}

fix(data);
fs.writeFileSync('openapi.yaml', JSON.stringify(data, null, 2));
