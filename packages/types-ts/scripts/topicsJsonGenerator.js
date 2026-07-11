import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { Topics } from '../topics';

const outputPath = path.resolve(__dirname, '..', '..', 'common', 'topics.json');

try {
  writeFileSync(outputPath, JSON.stringify(Topics, null, 2), 'utf-8');
  console.log(`Topics written to ${outputPath}`);
}
catch (err) {
  console.error(err);
}
