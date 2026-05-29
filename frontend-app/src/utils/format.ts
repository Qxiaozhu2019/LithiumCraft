export function formatDate(value?: string | null) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit"
  }).format(date);
}

export function splitTags(value?: string | null) {
  if (!value) return [];
  return value
    .split(/[,，;；\s]+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 6);
}
