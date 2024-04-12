<script lang="ts">
import {openDoor} from '../requests.ts';
import {dateNow} from '../lib/utils.ts';
import store from '../store/store.ts';
import {getCurrentlyValidDoors} from './doorAccess.ts';

let user
store.user.subscribe(v => user = v)

let accessibleDoors
function init() {
  const now = dateNow()
  accessibleDoors = getCurrentlyValidDoors(user, now)
}
init()


async function buttonPush(doorUuid) {
  const doorOpened: boolean = await openDoor(doorUuid)
  if (doorOpened) {
    // feedback success
  } else {
    // feedback failure
  }
}
</script>

<section id='door-buttons' class='flex flex-col gap-10'>
  {#if (accessibleDoors.length == 0)}
  <p>no permissions currently for this time and date</p>
  <p>{dateNow().toLocaleString()}</p>
  {/if}
  {#each [...accessibleDoors] as door}
    <button
      class='w-40 h-40 bg-yellow-900 border border-black shadow-md text-zinc-950 shadow-black rounded-2xl touch-pan-up hover:font-medium hover:translate-x-1 hover:rotate-1 hover:bg-yellow-950 focus:bg-lime-950'
      on:click={buttonPush(door.uuid)}
    >{door.name}</button>
  {/each}
</section>
