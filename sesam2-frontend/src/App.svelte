<script>
import Header from './Header.svelte';
import DoorButtons from './lib/DoorButtons.svelte';
import Footer from './Footer.svelte';
import LoginForm from './lib/LoginForm.svelte';
import Admin from './lib/Admin.svelte';
import store from './store/store.ts';

let loggedIn
store.loggedIn.subscribe((v) => {loggedIn = v})
let isAdmin
store.user.subscribe((v) => {isAdmin = v.is_admin})
</script>

<div 
  id='container'
  class='flex flex-col w-full min-h-full py-4 lg:w-2/3 xl:w-1/2 gap-8'>
  <Header loggedIn={loggedIn} />
  <main class='flex flex-col items-center gap-8'>
    {#if !loggedIn}
      <LoginForm />
    {:else}
      <DoorButtons />
      {#if isAdmin}
      <Admin />
      {/if}
    {/if}
  </main>
  <Footer />
</div>
