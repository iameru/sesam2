export function dateNow() {
  const now = new Date()
  now.setUTCHours(now.getUTCHours() + 2)
  now.toLocaleDateString()
  return now
}
