import fs from "fs";
const files = [
  "Header",
  "Hero",
  "Counter",
  "Pricing",
  "Contact",
  "Footer",
  "SpinWheel"
];
const dir = "./src/components/";

const template = (name) =>
`function ${name}() {
  return <div>${name} Works!</div>;
}
export default ${name};
`;

for (const f of files) {
  fs.writeFileSync(`${dir}${f}.jsx`, template(f));
}

console.log("✔ Components reset to working versions");
