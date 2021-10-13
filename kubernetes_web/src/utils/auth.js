import Cookies from 'js-cookie'

const TokenKey = 'Token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function getUsername(username) {
  return Cookies.get('username')
}

export function setUsername(username) {
  return Cookies.set('username', username)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}
