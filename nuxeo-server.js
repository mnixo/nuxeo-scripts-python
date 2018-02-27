const fs = require('fs');
const unzip = require('unzip');
const request = require('request');

console.log('nuxeo-server.js');

function getProgressBar(percent, sections) {
  const filledSections = Math.floor(percent * sections / 100);
  const emptySections = sections - filledSections;
  return `${'\u2588'.repeat(filledSections)}${'\u2591'.repeat(emptySections)}`;
}

function downloadFile(sourceUrl, destinationPath) {
  return new Promise(resolve => {
    console.log('downloadFile');
    let req = request({
      method: 'GET',
      uri: sourceUrl
    });
    req.pipe(fs.createWriteStream(destinationPath));
    req.on('response', data => {
      const total = data.headers['content-length'];
      let downloaded = 0;
      let lastPercent = -1;
      req.on('data', chunk => {
        downloaded += chunk.length;
        const percent = Math.round(10000 * downloaded / total) / 100;
        if (percent > lastPercent) {
          lastPercent = percent;
          //process.stdout.columns
          process.stdout.write(`Downloading: ${getProgressBar(percent, 100)} ${percent.toFixed(2)}%`);
          process.stdout.write(`Downloading: ${getProgressBar(percent, process.stdout.columns - 30)} ${percent.toFixed(2)}%`);
          process.stdout.write(percent < 100 ? '\r' : '\n');
        }
      });
    });
    req.on('end', () => resolve(destinationPath));
  });
}

function unzipFile(sourcePath, destinationPath) {
  return new Promise(resolve => {
    console.log('unzipFile');
    fs.createReadStream(sourcePath).pipe(unzip.Extract({
      path: destinationPath
    }).on('close', () => resolve(destinationPath)));
  });
}

let url = 'https://maven-eu.nuxeo.org/nexus/content/groups/public-snapshot/org/nuxeo/ecm/distribution/';
url += 'nuxeo-server-tomcat/10.1-SNAPSHOT/nuxeo-server-tomcat-10.1-20171216.073719-7.zip';

downloadFile(url, 'out.zip').then(filePath => {
  console.log(`filePath: ${filePath}`);
  return unzipFile(filePath, 'out')
}).then(unzippedPath => {
  console.log(`unzippedPath: ${unzippedPath}`);
  console.log('done')
});
