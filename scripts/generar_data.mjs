import fs from "node:fs/promises";
import path from "node:path";
import { Workbook } from "@oai/artifact-tool";

const ROOT = path.resolve(process.env.AGENTEWASI_ROOT || process.cwd());
const DATA_DIR = path.join(ROOT, "data");
const TMP_DIR = path.join(ROOT, "tmp", "spreadsheet_preview");
const SEED = 20260821;

function mulberry32(seed) {
  return function random() {
    let value = (seed += 0x6d2b79f5);
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  };
}

const random = mulberry32(SEED);
const randomInt = (min, max) => Math.floor(random() * (max - min + 1)) + min;

function pickWeighted(items, weightFor) {
  const weights = items.map(weightFor);
  const total = weights.reduce((sum, value) => sum + value, 0);
  let target = random() * total;
  for (let index = 0; index < items.length; index += 1) {
    target -= weights[index];
    if (target <= 0) return items[index];
  }
  return items.at(-1);
}

function csvEscape(value) {
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(headers, rows) {
  return [headers, ...rows]
    .map((row) => row.map(csvEscape).join(","))
    .join("\n") + "\n";
}

const products = [
  ["PROD-001", "Arroz extra 1 kg", "ABARROTES", "BOLSA", 5.20, 42, 20, true, 3.8],
  ["PROD-002", "Azúcar rubia 1 kg", "ABARROTES", "BOLSA", 4.80, 18, 15, true, 2.9],
  ["PROD-003", "Aceite vegetal 1 L", "ABARROTES", "BOTELLA", 10.90, 9, 12, true, 2.5],
  ["PROD-004", "Fideos spaghetti 500 g", "ABARROTES", "PAQUETE", 3.50, 34, 15, true, 3.2],
  ["PROD-005", "Atún en lata 170 g", "ABARROTES", "LATA", 6.90, 0, 10, true, 1.6],
  ["PROD-006", "Agua mineral 625 ml", "BEBIDAS", "BOTELLA", 2.00, 55, 20, true, 4.2],
  ["PROD-007", "Gaseosa cola 500 ml", "BEBIDAS", "BOTELLA", 3.50, 21, 15, true, 3.7],
  ["PROD-008", "Gaseosa naranja 500 ml", "BEBIDAS", "BOTELLA", 3.20, 14, 12, true, 2.6],
  ["PROD-009", "Néctar de durazno 1 L", "BEBIDAS", "CAJA", 5.90, 6, 8, true, 1.7],
  ["PROD-010", "Bebida rehidratante 500 ml", "BEBIDAS", "BOTELLA", 4.00, 32, 12, true, 2.4],
  ["PROD-011", "Leche evaporada 400 g", "LACTEOS", "LATA", 4.50, 8, 10, true, 4.0],
  ["PROD-012", "Yogur fresa 1 L", "LACTEOS", "BOTELLA", 7.90, 16, 12, true, 2.0],
  ["PROD-013", "Yogur bebible 180 ml", "LACTEOS", "BOTELLA", 2.20, 28, 15, true, 2.8],
  ["PROD-014", "Queso fresco 250 g", "LACTEOS", "PAQUETE", 9.50, 0, 6, true, 1.2],
  ["PROD-015", "Mantequilla 200 g", "LACTEOS", "PAQUETE", 8.90, 8, 8, true, 1.3],
  ["PROD-016", "Detergente 800 g", "LIMPIEZA", "BOLSA", 11.50, 7, 10, true, 1.4],
  ["PROD-017", "Lavavajilla 750 ml", "LIMPIEZA", "BOTELLA", 8.50, 14, 10, true, 1.2],
  ["PROD-018", "Lejía 1 L", "LIMPIEZA", "BOTELLA", 4.20, 24, 10, true, 1.5],
  ["PROD-019", "Papel higiénico 4 rollos", "LIMPIEZA", "PAQUETE", 8.90, 18, 12, true, 1.9],
  ["PROD-020", "Limpiatodo 900 ml", "LIMPIEZA", "BOTELLA", 6.50, 0, 8, true, 1.0],
  ["PROD-021", "Champú 400 ml", "CUIDADO_PERSONAL", "BOTELLA", 14.90, 5, 7, true, 0.06],
  ["PROD-022", "Jabón de tocador", "CUIDADO_PERSONAL", "UNIDAD", 3.20, 27, 12, true, 1.6],
  ["PROD-023", "Pasta dental 90 ml", "CUIDADO_PERSONAL", "UNIDAD", 7.50, 13, 10, true, 1.1],
  ["PROD-024", "Desodorante 150 ml", "CUIDADO_PERSONAL", "UNIDAD", 12.90, 18, 8, true, 0.05],
  ["PROD-025", "Toallas higiénicas 10 unidades", "CUIDADO_PERSONAL", "PAQUETE", 8.20, 0, 8, true, 0],
  ["PROD-026", "Galletas de vainilla", "SNACKS", "PAQUETE", 1.50, 60, 20, true, 4.1],
  ["PROD-027", "Papas fritas 45 g", "SNACKS", "BOLSA", 2.50, 17, 15, true, 3.0],
  ["PROD-028", "Chocolate 30 g", "SNACKS", "UNIDAD", 2.00, 10, 10, true, 2.7],
  ["PROD-029", "Caramelos surtidos 100 g", "SNACKS", "BOLSA", 2.80, 38, 15, true, 2.5],
  ["PROD-030", "Maní salado 100 g", "SNACKS", "BOLSA", 3.50, 0, 8, true, 0.04],
  ["PROD-031", "Pan francés", "PANADERIA", "UNIDAD", 0.40, 85, 30, true, 5.2],
  ["PROD-032", "Pan integral 500 g", "PANADERIA", "PAQUETE", 6.50, 11, 10, true, 1.4],
  ["PROD-033", "Queque de vainilla 400 g", "PANADERIA", "PAQUETE", 9.90, 5, 6, true, 1.0],
  ["PROD-034", "Bizcochos 6 unidades", "PANADERIA", "PAQUETE", 4.50, 22, 10, true, 1.7],
  ["PROD-035", "Tostadas 200 g", "PANADERIA", "PAQUETE", 4.20, 0, 7, true, 0],
].map(([id, name, category, unit, price, stock, minimum, active, weight]) => ({
  id, name, category, unit, price, stock, minimum, active, weight,
}));

const firstNames = [
  "Rosa", "José", "María", "Luis", "Carmen", "Carlos", "Ana", "Jorge", "Lucía", "Miguel",
  "Elena", "Pedro", "Patricia", "Juan", "Milagros", "Víctor", "Claudia", "Renzo", "Diana", "Marco",
];
const lastNames = ["Mendoza", "García", "Castro", "Díaz", "Rojas"];
const customers = [];
for (let index = 0; index < 100; index += 1) {
  const id = `CLI-${String(index + 1).padStart(3, "0")}`;
  const name = `${firstNames[index % firstNames.length]} ${lastNames[Math.floor(index / firstNames.length)]}`;
  const segment = index < 15 ? "ALTA" : index < 70 ? "MEDIA" : "OCASIONAL";
  const weight = segment === "ALTA" ? 5 : segment === "MEDIA" ? 2.2 : 0.8;
  customers.push({ id, name, segment, weight });
}

function seasonalWeight(product, month, dateKey) {
  let factor = 1;
  if ([1, 2].includes(month) && product.category === "BEBIDAS") factor *= 1.65;
  if (month === 3 && ["CUIDADO_PERSONAL", "SNACKS"].includes(product.category)) factor *= 1.25;
  if (month === 7 && dateKey >= "2026-07-24" && dateKey <= "2026-07-30") {
    if (["BEBIDAS", "SNACKS", "ABARROTES"].includes(product.category)) factor *= 1.45;
  }
  return product.weight * factor;
}

function historicalPrice(product, month) {
  const factor = month <= 2 ? 0.94 : month <= 4 ? 0.97 : month <= 6 ? 0.99 : 1;
  return Number((product.price * factor).toFixed(2));
}

const salesRows = [];
const startDate = new Date(Date.UTC(2026, 0, 1));
const endDate = new Date(Date.UTC(2026, 7, 21));
let saleNumber = 0;

for (let date = new Date(startDate); date <= endDate; date.setUTCDate(date.getUTCDate() + 1)) {
  const dateKey = date.toISOString().slice(0, 10);
  const dayOfWeek = date.getUTCDay();
  const isWeekendWindow = [0, 5, 6].includes(dayOfWeek);
  const saleCount = isWeekendWindow ? randomInt(18, 30) : randomInt(12, 20);
  const month = date.getUTCMonth() + 1;

  for (let dailyIndex = 0; dailyIndex < saleCount; dailyIndex += 1) {
    saleNumber += 1;
    const saleId = `VTA-${String(saleNumber).padStart(6, "0")}`;
    const customer = saleNumber <= customers.length
      ? customers[saleNumber - 1]
      : pickWeighted(customers, (item) => item.weight);
    const method = pickWeighted(
      ["EFECTIVO", "YAPE", "PLIN", "TARJETA"],
      (item) => ({ EFECTIVO: 45, YAPE: 30, PLIN: 15, TARJETA: 10 })[item],
    );
    const hour = randomInt(7, 21);
    const minute = randomInt(0, 59);
    const second = randomInt(0, 59);
    const time = `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}:${String(second).padStart(2, "0")}`;
    const lineCount = pickWeighted([1, 2, 3, 4, 5], (item) => ({ 1: 30, 2: 32, 3: 22, 4: 11, 5: 5 })[item]);
    const selected = [];

    while (selected.length < lineCount) {
      const available = products.filter((product) => product.weight > 0 && !selected.includes(product));
      selected.push(pickWeighted(available, (product) => seasonalWeight(product, month, dateKey)));
    }

    for (const product of selected) {
      const maxQuantity = product.id === "PROD-031" ? 20 : 6;
      const quantity = product.id === "PROD-031" ? randomInt(2, maxQuantity) : randomInt(1, maxQuantity);
      const unitPrice = historicalPrice(product, month);
      const gross = quantity * unitPrice;
      const hasDiscount = random() < 0.10;
      const discountRate = hasDiscount ? 0.02 + random() * 0.13 : 0;
      const discount = Number((gross * discountRate).toFixed(2));
      salesRows.push([
        saleId,
        dateKey,
        time,
        customer.id,
        customer.name,
        product.id,
        quantity,
        unitPrice.toFixed(2),
        discount.toFixed(2),
        method,
      ]);
    }
  }
}

const salesHeaders = [
  "venta_id", "fecha", "hora", "cliente_id", "cliente_nombre",
  "producto_id", "cantidad", "precio_unitario", "descuento", "metodo_pago",
];
const inventoryHeaders = [
  "producto_id", "producto", "categoria", "unidad_medida",
  "precio_venta_actual", "stock_actual", "stock_minimo", "activo",
];
const inventoryRows = products.map((product) => [
  product.id,
  product.name,
  product.category,
  product.unit,
  product.price.toFixed(2),
  product.stock,
  product.minimum,
  product.active ? "TRUE" : "FALSE",
]);

const salesCsv = toCsv(salesHeaders, salesRows);
const inventoryCsv = toCsv(inventoryHeaders, inventoryRows);

await fs.mkdir(DATA_DIR, { recursive: true });
await fs.mkdir(TMP_DIR, { recursive: true });
await fs.writeFile(path.join(DATA_DIR, "ventas_ejemplo.csv"), salesCsv, "utf8");
await fs.writeFile(path.join(DATA_DIR, "inventario_ejemplo.csv"), inventoryCsv, "utf8");

// Required spreadsheet-level validation and visual inspection.
const salesWorkbook = await Workbook.fromCSV(salesCsv, { sheetName: "Ventas" });
const inventoryWorkbook = await Workbook.fromCSV(inventoryCsv, { sheetName: "Inventario" });
const salesSheet = salesWorkbook.worksheets.getItem("Ventas");
const inventorySheet = inventoryWorkbook.worksheets.getItem("Inventario");
const salesWidths = [15, 12, 10, 12, 21, 13, 10, 16, 12, 15];
const inventoryWidths = [13, 30, 19, 17, 20, 13, 13, 10];
salesWidths.forEach((width, index) => {
  salesSheet.getRangeByIndexes(0, index, salesRows.length + 1, 1).format.columnWidth = width;
});
inventoryWidths.forEach((width, index) => {
  inventorySheet.getRangeByIndexes(0, index, inventoryRows.length + 1, 1).format.columnWidth = width;
});
salesSheet.getRange("A1:J1").format = { fill: "#0F766E", font: { bold: true, color: "#FFFFFF" } };
inventorySheet.getRange("A1:H1").format = { fill: "#0F766E", font: { bold: true, color: "#FFFFFF" } };
salesSheet.freezePanes.freezeRows(1);
inventorySheet.freezePanes.freezeRows(1);
const salesInspect = await salesWorkbook.inspect({
  kind: "table",
  range: "Ventas!A1:J8",
  include: "values",
  tableMaxRows: 8,
  tableMaxCols: 10,
});
const inventoryInspect = await inventoryWorkbook.inspect({
  kind: "table",
  range: "Inventario!A1:H12",
  include: "values",
  tableMaxRows: 12,
  tableMaxCols: 8,
});
const salesPreview = await salesWorkbook.render({ sheetName: "Ventas", range: "A1:J20", scale: 1.3, format: "png" });
const inventoryPreview = await inventoryWorkbook.render({ sheetName: "Inventario", range: "A1:H20", scale: 1.3, format: "png" });
await fs.writeFile(path.join(TMP_DIR, "ventas_preview.png"), new Uint8Array(await salesPreview.arrayBuffer()));
await fs.writeFile(path.join(TMP_DIR, "inventario_preview.png"), new Uint8Array(await inventoryPreview.arrayBuffer()));

function stockState(product) {
  if (product.stock === 0) return "AGOTADO";
  if (product.stock <= product.minimum) return "CRITICO";
  if (product.stock <= product.minimum * 1.5) return "BAJO";
  return "NORMAL";
}

const saleIds = new Set();
const customerIds = new Set();
const soldProductIds = new Set();
const monthlySales = {};
const clientNames = new Map();
const saleFacts = new Map();
let totalNet = 0;

for (const row of salesRows) {
  const [saleId, dateKey, time, customerId, customerName, productId, quantity, unitPrice, discount, method] = row;
  saleIds.add(saleId);
  customerIds.add(customerId);
  soldProductIds.add(productId);
  monthlySales[dateKey.slice(0, 7)] = (monthlySales[dateKey.slice(0, 7)] ?? new Set()).add(saleId);
  totalNet += Number(quantity) * Number(unitPrice) - Number(discount);
  if (clientNames.has(customerId) && clientNames.get(customerId) !== customerName) throw new Error(`Nombre inconsistente para ${customerId}`);
  clientNames.set(customerId, customerName);
  const fact = `${dateKey}|${time}|${customerId}|${customerName}|${method}`;
  if (saleFacts.has(saleId) && saleFacts.get(saleId) !== fact) throw new Error(`Cabecera inconsistente para ${saleId}`);
  saleFacts.set(saleId, fact);
  if (!products.some((product) => product.id === productId)) throw new Error(`Producto inexistente ${productId}`);
  if (Number(quantity) <= 0 || Number(unitPrice) <= 0 || Number(discount) < 0) throw new Error(`Importe inválido en ${saleId}`);
}

const states = products.reduce((accumulator, product) => {
  const state = stockState(product);
  accumulator[state] = (accumulator[state] ?? 0) + 1;
  return accumulator;
}, {});
const zeroSales = products.filter((product) => !soldProductIds.has(product.id)).map((product) => product.id);
const monthlyCounts = Object.fromEntries(Object.entries(monthlySales).map(([month, ids]) => [month, ids.size]));

const assertions = {
  startDate: salesRows[0][1] === "2026-01-01",
  endDate: salesRows.at(-1)[1] === "2026-08-21",
  customerCount: customerIds.size === 100,
  productCount: products.length === 35,
  zeroSalesProducts: zeroSales.length === 2,
  stockStates: JSON.stringify(states) === JSON.stringify({ NORMAL: 12, BAJO: 9, CRITICO: 8, AGOTADO: 6 }),
  expectedMonths: Object.keys(monthlyCounts).length === 8,
};
for (const [name, valid] of Object.entries(assertions)) {
  if (!valid) throw new Error(`Validación fallida: ${name}`);
}

const summary = {
  seed: SEED,
  period: { start: "2026-01-01", end: "2026-08-21" },
  sales: saleIds.size,
  salesRows: salesRows.length,
  customers: customerIds.size,
  products: products.length,
  totalNetSales: Number(totalNet.toFixed(2)),
  zeroSalesProducts: zeroSales,
  stockStates: states,
  monthlySales: monthlyCounts,
  validations: assertions,
  artifactInspection: {
    sales: salesInspect.ndjson.split("\n").slice(0, 3),
    inventory: inventoryInspect.ndjson.split("\n").slice(0, 3),
  },
};
await fs.writeFile(path.join(TMP_DIR, "resumen_generacion.json"), JSON.stringify(summary, null, 2), "utf8");
console.log(JSON.stringify(summary, null, 2));
