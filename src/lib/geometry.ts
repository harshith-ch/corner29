// 0° heading = screen-up, clockwise positive. Caller rotates the containing
// element; this path is drawn centered at the origin pointing up so rotation
// works without any translation offset.
export function conePath(angle: number, radius: number): string {
  const half = (angle / 2) * (Math.PI / 180);
  const x1 = -Math.sin(half) * radius;
  const y1 = -Math.cos(half) * radius;
  const x2 = Math.sin(half) * radius;
  const y2 = -Math.cos(half) * radius;
  const large = angle > 180 ? 1 : 0;
  return `M0 0 L${x1.toFixed(2)} ${y1.toFixed(2)} A${radius} ${radius} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)} Z`;
}

export function pct(value: number, origin: number, extent: number): number {
  return ((value - origin) / extent) * 100;
}
