import { writable } from 'svelte/store'


function load(key: string): any {
  return JSON.parse(localStorage.getItem(key) || 'null')
}

type doorGrant = {
  door_uuid: string
  weekday: number
  grant_start: string
  grant_end: string
}
type user = {
  name: string,
  exp: number,
  door_grants: doorGrant[],
  is_admin: boolean,
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
    localStorage.setItem("user", value ? JSON.stringify(value): JSON.stringify(null));
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

