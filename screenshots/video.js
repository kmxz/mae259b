// use ffmpeg to join images to video

const fs = require('fs');
const cp = require('child_process');

const prefix = process.argv[2];

if (!prefix) { throw 'No prefix specified.'; }

const rd = Math.random().toString(36).substr(2, 6) + '-';

const mvs = fs.readdirSync('.').filter(_ => _.startsWith(prefix)).map((f, i) => new Promise((res, rej) =>
	cp.exec('mv '+ f + ' ' + rd + (String(i).length === 1 ? '0' + i : i) + '.png', {}, err => {
		if (err) { rej(err); } else { res(); }
	})
));

Promise.all(mvs).then(() =>
	cp.exec('ffmpeg -framerate 15 -i ' + rd + '%02d.png ' + rd + 'output.mp4', {}, (error, stdout, stderr) => {
		console.log(stdout);
		console.log('Output file: ' + rd + 'output.mp4');
	})
);
