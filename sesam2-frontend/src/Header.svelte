<script>
export let loggedIn
import store from './store/store.ts';

function handleClick() {
  store.loggedIn.set(false)
}

let username
store.user.subscribe(v => {
  username = v.name
})

function randomGreeting(username) {
  const greetings = [
    'Hello ',
    'Hi there ',
    'Welcome back ',
    'Greetings ',
    'Howdy ',
  ];
  return greetings[Math.floor(Math.random() * greetings.length)] + username + "!";
}
</script>

<header class='flex flex-row items-center justify-end p-4 gap-2'>
  {#if loggedIn}
  <p>{randomGreeting(username)}</p>
  <button class='px-2 py-1 border rounded border-zinc-700 text-zinc-400'
      on:click={handleClick}
    >log out</button>
  {/if}
</header>
