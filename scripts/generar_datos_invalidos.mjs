import fs from "node:fs/promises";
import path from "node:path";
import { Workbook } from "@oai/artifact-tool";

const root = path.resolve(process.env.AGENTEWASI_ROOT || process.cwd());
const dataDir = path.join(root, "data");
const previewDir = path.join(root, "tmp", "spreadsheet_preview");
const outputPath = path.join(dataDir, "datos_invalidos_columnas.csv");

// La columna obligatoria `cantidad` se omite intencionalmente.
const headers = [
  "venta_id",
  "fecha",
  "hora",
  "cliente_id",
  "cliente_nombre",
  "producto_id",
  "precio_unitario",
  "descuento",
  "metodo_pago",
];

const rows = [
  ["VTA-ERROR-001", "2026-08-21", "09:15:00", "CLI-001", "Rosa Mendoza", "PROD-001", "5.20", "0.00", "EFECTIVO"],
  ["VTA-ERROR-002", "2026-08-21", "10:30:00", "CLI-002", "José Mendoza", "PROD-006", "2.00", "0.00", "YAPE"],
  ["VTA-ERROR-003", "2026-08-21", "11:45:00", "CLI-003", "María Mendoza", "PROD-011", "4.50", "0.50", "PLIN"],
  ["VTA-ERROR-004", "2026-08-21", "12:20:00", "CLI-004", "Luis Mendoza", "PROD-026", "1.50", "0.00", "TARJETA"],
];

const csv = [headers, ...rows].map((row) => row.join(",")).join("\n") + "\n";
await fs.mkdir(dataDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });
await fs.writeFile(outputPath, csv, "utf8");

const requiredHeaders = [
  "venta_id",
  "fecha",
  "hora",
  "cliente_id",
  "cliente_nombre",
  "producto_id",
  "cantidad",
  "precio_unitario",
  "descuento",
  "metodo_pago",
];
const missing = requiredHeaders.filter((header) => !headers.includes(header));
const unexpected = headers.filter((header) => !requiredHeaders.includes(header));
if (missing.length !== 1 || missing[0] !== "cantidad") {
  throw new Error(`Se esperaba únicamente la columna faltante cantidad: ${missing.join(",")}`);
}
if (unexpected.length !== 0) {
  throw new Error(`Columnas inesperadas: ${unexpected.join(",")}`);
}

const workbook = await Workbook.fromCSV(csv, { sheetName: "DatosInvalidos" });
const sheet = workbook.worksheets.getItem("DatosInvalidos");
const widths = [17, 13, 11, 12, 21, 13, 16, 12, 15];
widths.forEach((width, index) => {
  sheet.getRangeByIndexes(0, index, rows.length + 1, 1).format.columnWidth = width;
});
sheet.getRange("A1:I1").format = { fill: "#B91C1C", font: { bold: true, color: "#FFFFFF" } };
sheet.freezePanes.freezeRows(1);

const inspection = await workbook.inspect({
  kind: "table",
  range: "DatosInvalidos!A1:I5",
  include: "values",
  tableMaxRows: 5,
  tableMaxCols: 9,
});
const preview = await workbook.render({
  sheetName: "DatosInvalidos",
  range: "A1:I5",
  scale: 1.5,
  format: "png",
});
await fs.writeFile(
  path.join(previewDir, "datos_invalidos_preview.png"),
  new Uint8Array(await preview.arrayBuffer()),
);

console.log(JSON.stringify({
  output: outputPath,
  rows: rows.length,
  missingColumns: missing,
  unexpectedColumns: unexpected,
  inspection: inspection.ndjson,
}, null, 2));
