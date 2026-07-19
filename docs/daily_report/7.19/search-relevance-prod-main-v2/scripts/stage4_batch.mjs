import { collectQuery } from "./collector.mjs";
import fs from "fs";

const BASE_URL = process.argv[2] || "http://localhost:4501";
const OUT = process.argv[3] || "/tmp/stage4_v0.json";

const CASES = [
  // 4 known net-negative bug cases (V1 historical)
  { id: "V125", query: "烘焙包装", group: "net_negative" },
  { id: "V127", query: "咖啡馆菜单", group: "net_negative" },
  { id: "V153", query: "饮料瓶", group: "net_negative" },
  { id: "V271", query: "课程表", group: "net_negative" },
  // substring / ambiguity
  { id: "SUB_01", query: "coffee cup", group: "substring_ambiguity" },
  { id: "SUB_02", query: "咖啡杯", group: "substring_ambiguity" },
  { id: "SUB_03", query: "black friday banner", group: "substring_ambiguity" },
  { id: "SUB_04", query: "charm", group: "substring_ambiguity" },
  { id: "SUB_05", query: "标志", group: "substring_ambiguity" },
  { id: "SUB_06", query: "迷你手办", group: "substring_ambiguity" },
  { id: "SUB_07", query: "periodic table", group: "substring_ambiguity" },
  { id: "SUB_08", query: "元素周期表", group: "substring_ambiguity" },
  // rewrite flooding
  { id: "FLOOD_01", query: "globe", group: "rewrite_flooding" },
  { id: "FLOOD_02", query: "statue", group: "rewrite_flooding" },
  { id: "FLOOD_03", query: "plush pillow", group: "rewrite_flooding" },
  { id: "FLOOD_04", query: "drink bottle", group: "rewrite_flooding" },
  { id: "FLOOD_05", query: "bobblehead", group: "rewrite_flooding" },
  // broad noise templates
  { id: "NOISE_01", query: "吉祥物", group: "broad_noise" },
  { id: "NOISE_02", query: "元素周期表", group: "broad_noise" },
  { id: "NOISE_03", query: "periodic table", group: "broad_noise" },
  { id: "NOISE_04", query: "贴纸", group: "broad_noise" },
  { id: "NOISE_05", query: "logo", group: "broad_noise" },
  { id: "NOISE_06", query: "横幅", group: "broad_noise" },
];

const results = [];
for (const c of CASES) {
  const r = await collectQuery(BASE_URL, c.query, { locale: "en" });
  results.push({ ...c, ...r });
  console.log(`${c.id}\t${c.query}\tok=${r.ok}\tinsp=${r.inspirationCount}\ttpl=${r.matchedTemplateCount}\ttotal=${r.totalResults}\trewrites=${JSON.stringify(r.usedRewrites)}\tpaths=${r.pathsUsed}`);
}
fs.writeFileSync(OUT, JSON.stringify(results, null, 2));
console.log(`\nWrote ${results.length} results to ${OUT}`);
