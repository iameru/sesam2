import { writable } from 'svelte/store'
import type { UserType } from '../lib/types'


function load(key: string): any {
  return JSON.parse(localStorage.getItem(key) || 'null')
}

const defaultUser: UserType = {
  name: '',
  exp: 0,
  door_grants: [],
  is_admin: false,
}


const serverOnline = writable(load('serverOnline') || false)

const loggedIn = writable(load('loggedIn') || false)
loggedIn.subscribe(value => {
    localStorage.setItem("loggedIn", value ? 'true' : 'false');
});

const accessToken = writable(load('accessToken') || null)
accessToken.subscribe(value => {
    localStorage.setItem("accessToken", value ? JSON.stringify(value): JSON.stringify(null));
});

const user = writable(load('user') || null)
user.subscribe(value => {
    localStorage.setItem("user", value ? JSON.stringify(value): JSON.stringify(defaultUser));
})

type Store = {
  loggedIn: typeof loggedIn,
  serverOnline: typeof serverOnline,
  accessToken: typeof accessToken,
  user: typeof user,

}
const store: Store = {
  loggedIn,
  serverOnline,
  accessToken,
  user,
}
export default store
