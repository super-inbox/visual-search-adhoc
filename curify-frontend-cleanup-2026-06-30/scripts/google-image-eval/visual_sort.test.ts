/**
 * Simple tests for the visualSort function.
 * Run with: npx tsx scripts/google-image-eval/visual_sort.test.ts
 */
import { testableVisualSort } from "./extractResults.js";

// Each fake "element" is just an object with a bbox and thumbnail
function makeItem(x: number, y: number, w = 100, h = 100) {
  return {
    el: {} as never,
    bbox: { x, y, width: w, height: h },
    thumbnailUrl: `http://example.com/${x}-${y}.jpg`,
  };
}

let passed = 0;
let failed = 0;

function test(name: string, fn: () => void) {
  try {
    fn();
    console.log(`✓ ${name}`);
    passed++;
  } catch (err) {
    console.log(`✗ ${name}: ${(err as Error).message}`);
    failed++;
  }
}

function assert(condition: boolean, msg: string) {
  if (!condition) throw new Error(msg);
}

// ── Tests ──────────────────────────────────────────────────────────────────

test("single item", () => {
  const items = [makeItem(100, 200)];
  const sorted = testableVisualSort(items);
  assert(sorted.length === 1, "should have 1 item");
  assert(sorted[0].bbox.x === 100, "x should be 100");
});

test("two rows sorted top to bottom", () => {
  const row2 = makeItem(100, 300);
  const row1 = makeItem(100, 100);
  const sorted = testableVisualSort([row2, row1]);
  assert(sorted[0].bbox.y === 100, "first should be top row");
  assert(sorted[1].bbox.y === 300, "second should be bottom row");
});

test("same row sorted left to right", () => {
  const right = makeItem(500, 100);
  const left = makeItem(50, 100);
  const sorted = testableVisualSort([right, left]);
  assert(sorted[0].bbox.x === 50, "first should be leftmost");
  assert(sorted[1].bbox.x === 500, "second should be rightmost");
});

test("filters out tiny elements", () => {
  const tiny = makeItem(100, 100, 20, 20); // smaller than MIN_IMAGE_SIZE
  const normal = makeItem(200, 100, 150, 150);
  const sorted = testableVisualSort([tiny, normal]);
  assert(sorted.length === 1, "tiny element should be filtered");
  assert(sorted[0].bbox.x === 200, "should keep normal element");
});

test("filters negative-position elements", () => {
  const offscreen = makeItem(-100, -100);
  const onscreen = makeItem(100, 100);
  const sorted = testableVisualSort([offscreen, onscreen]);
  assert(sorted.length === 1, "offscreen element should be filtered");
});

test("3x3 grid left-to-right top-to-bottom", () => {
  const items = [
    makeItem(0, 0),
    makeItem(150, 0),
    makeItem(300, 0),
    makeItem(0, 150),
    makeItem(150, 150),
    makeItem(300, 150),
    makeItem(0, 300),
    makeItem(150, 300),
    makeItem(300, 300),
  ];
  // Shuffle
  const shuffled = items.sort(() => Math.random() - 0.5);
  const sorted = testableVisualSort(shuffled);
  assert(sorted.length === 9, "all 9 items");
  // First row: x=0, x=150, x=300 all at y=0
  assert(sorted[0].bbox.y === 0, "first item in first row");
  assert(sorted[0].bbox.x === 0, "first item leftmost");
  assert(sorted[2].bbox.x === 300, "third item rightmost in first row");
  // Last row
  assert(sorted[8].bbox.y === 300, "last item in last row");
  assert(sorted[8].bbox.x === 300, "last item rightmost");
});

test("y-tolerance groups items in same row", () => {
  // Items with slightly different Y values should be in the same row
  const a = makeItem(100, 100);
  const b = makeItem(200, 110); // 10px off, within tolerance of 30
  const c = makeItem(300, 95);
  const sorted = testableVisualSort([a, b, c]);
  assert(sorted.length === 3, "all items kept");
  // Should be in left-to-right order (same row)
  assert(sorted[0].bbox.x === 100, "leftmost first");
  assert(sorted[1].bbox.x === 200, "middle second");
  assert(sorted[2].bbox.x === 300, "rightmost third");
});

// ── Summary ─────────────────────────────────────────────────────────────────

console.log(`\n${passed} passed, ${failed} failed`);
if (failed > 0) process.exit(1);
