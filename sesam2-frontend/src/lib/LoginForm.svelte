<script>
import store from '../store/store.ts';
import {makeLoginRequest} from '../requests.ts';
let username
let password

let serverOnline
store.serverOnline.subscribe((v) => { serverOnline = v })
let loggedIn
store.loggedIn.subscribe((v) => { loggedIn = v })

async function handleOnSubmit() {
  await makeLoginRequest(username, password)
}
</script>

{#if !serverOnline}
<p class='font-light'>server offline :(</p>
{:else}
<form
  id='log-in'
  class='flex flex-col text-center gap-2'
  on:submit|preventDefault={handleOnSubmit}
>
  <p>please log in</p>
  <input class='p-1 text-black rounded bg-zinc-300' placeholder='username' bind:value={username} />
  <input class='p-1 text-black rounded bg-zinc-300' placeholder='password' bind:value={password} />
  <button class='px-4 py-2 rounded bg-zinc-800'
  >log in now</button>
</form>
{/if}
