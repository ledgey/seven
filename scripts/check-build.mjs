import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import { resolve } from 'node:path';

const html = await readFile('dist/index.html', 'utf8');
assert(!html.includes('{%'), 'Unconverted Django template tag');
const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(m => m[1]));
for (const [, attribute, value] of html.matchAll(/\b(src|href)="([^"]+)"/g)) {
  if (value.startsWith('#')) {
    if (value.length > 1) assert(ids.has(value.slice(1)), `Missing anchor ${value}`);
  } else if (value.startsWith('/')) {
    await access(resolve('dist', value.slice(1).split('?')[0]));
  }
}
assert(html.includes('27 West Main Street') && html.includes('EH52 5DN'));
assert.equal((html.match(/7\.30am–3pm/g) || []).length, 2);
assert.equal((html.match(/8\.30am–3pm/g) || []).length, 2);
for (const profile of ['seven_belfast/', 'sevencoffeebelfast', 'seven_coffee_west_lothian/', 'facebook.com/profile.php?id=61595368988527']) {
  assert(html.includes(profile), `Missing social profile ${profile}`);
}
assert(html.includes('Always dog friendly.'));
assert(html.includes('Irish and local suppliers'));
console.log('PASS: built assets, section links, both locations, hours and social profiles');
