const TOKEN_KEY = 'ne_oynasam_token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

export class ApiError extends Error {
  constructor(status, detail) {
    super(detail || `HTTP ${status}`)
    this.status = status
  }
}

export async function api(path, { method = 'GET', body, form, auth = true } = {}) {
  const headers = {}
  try { headers['Accept-Language'] = localStorage.getItem('ne_oynasam_lang') || 'tr' } catch { /* yoksay */ }
  if (auth && getToken()) headers.Authorization = `Bearer ${getToken()}`
  let payload
  if (form) payload = new URLSearchParams(form)
  else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    payload = JSON.stringify(body)
  }
  const res = await fetch(path, { method, headers, body: payload })
  if (res.status === 401 && auth) {
    clearToken()
    window.dispatchEvent(new Event('auth:expired'))
    throw new ApiError(401, 'Oturum süresi doldu')
  }
  if (res.status === 204) return null
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(res.status, data?.detail)
  return data
}
