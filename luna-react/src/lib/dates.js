export function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

export function getMonday(d) {
  const x = new Date(d);
  const day = x.getDay();
  const diff = x.getDate() - (day === 0 ? 7 : day) + 1;
  return new Date(x.getFullYear(), x.getMonth(), diff);
}
