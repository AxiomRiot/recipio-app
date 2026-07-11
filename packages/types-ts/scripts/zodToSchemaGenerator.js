import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { z } from 'zod';
import { EventSchemasByTopic } from '../events';

const outputDir = path.resolve(__dirname, '..', '..', 'common', 'events');

function splitPascal(str) {
  return str
    .split(/[-_\s]+/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

for (const [topic, eventSchema] of Object.entries(EventSchemasByTopic)) {
  const outputFile = `${splitPascal(topic)}Event`;
  const outputPath = path.join(outputDir, `${outputFile}.json`);
  const jsonSchema = z.toJSONSchema(eventSchema);

  try {
    writeFileSync(outputPath, JSON.stringify(jsonSchema, null, 2), 'utf-8');
    console.log(`Schema written to ${outputPath}`);
  }
  catch (err) {
    console.error(err);
  }
}
